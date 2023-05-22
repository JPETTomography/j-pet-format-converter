# Wrtier module
#Author: Mateusz Kruk, Rafal Mozdzonek

from datetime import datetime
import logging
import os
from pathlib import Path
import random
from typing import Union

from numpy.core.records import array
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid

from converter.exceptions import InterfileDataMissingException
from converter.reader import read_binary
from converter.settings import UID
from models.metadata import InterfileHeader, CTMetaFile, PETMetaFile
from models.metadata import PatientData, PetSeries


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


def rand_uid(prefix: str=UID) -> str:
    return str(generate_uid(
        prefix=prefix,
        entropy_srcs=[str(random.getrandbits(100))]
    ))


def add_from_interfile_header(obj: InterfileHeader, dataset: Dataset) -> Dataset:
    """
        Writes interfile meta data from header dictionary to dicom dataset.

        Arguments:
        obj - InterfileHeader obj
        dataset - dicom dataset

        Returns:
        dataset - dicom dataset with inserted header values
    """

    dataset.Modality = obj.modality

    dataset.PixelSpacing = [obj.scaling_factor_1, obj.scaling_factor_2]
    dataset.SliceThickness = obj.scaling_factor_3

    dataset.RescaleIntercept = obj.data_rescale_offset
    dataset.RescaleSlope = obj.data_rescale_slope

    return dataset

def add_from_json(obj: Union[CTMetaFile, PETMetaFile], dataset: Dataset) -> Dataset:
    """
        Writes json meta data to dicom dataset.

        Arguments:
        obj - MetaFile object
        dataset - dicom dataset

        Returns:
        dataset - dicom dataset with inserted values
    """
    tags = []
    if dataset.Modality == "CT":
        assert isinstance(obj, CTMetaFile)
        tags = CTMetaFile.get_field_names()
    if dataset.Modality == "PT":
        assert isinstance(obj, PETMetaFile)
        tags = PETMetaFile.get_field_names()

    tags = filter(lambda k: k[0].isupper(), tags)

    for tag in tags:
        # Convert Tuple to List (for pydicom purposes)
        val = list(obj[tag]) if isinstance(obj[tag], tuple) else obj[tag]
        # Set DICOM Attribute
        setattr(dataset, tag, val)

    patient_tags = PatientData.get_field_names()
    patient_tags = filter(lambda k: k[0].isupper(), patient_tags)

    for patient_tag in patient_tags:
        setattr(dataset, patient_tag, obj.patient[patient_tag])

    if isinstance(obj, PETMetaFile):
        pet_series_tags = PetSeries.get_field_names()
        pet_series_tags = filter(lambda k: k[0].isupper(), pet_series_tags)

        for pet_series_tag in pet_series_tags:
            setattr(dataset, pet_series_tag, obj.petSeries[pet_series_tag])

        # TODO: Parse this from metafile
        dataset.RadiopharmaceuticalInformationSequence = Sequence()
        dataset.PatientOrientationCodeSequence = Sequence()
        dataset.PatientGantryRelationshipCodeSequence = Sequence()

    return dataset

def add_dicom_metadata(dataset: Dataset) -> Dataset:
    file_meta = FileMetaDataset()
    """A Transfer Syntax is a set of encoding rules able to unambiguously represent one or more
    Abstract Syntaxes. In particular, it allows communicating Application Entities to negotiate
    common encoding techniques they both support (e.g., byte ordering, compression, etc.).
    A Transfer Syntax is an attribute of a Presentation Context, one or more of which are
    negotiated at the establishment of an Association between DICOM Application Entities."""
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1' # Explicit VR Little Endian

    file_meta.ImplementationVersionName = 'J-PET_V0'

    dataset.file_meta = file_meta

    return dataset

def interfile_image_to_dicom_dataset(
    obj: InterfileHeader,
    binary_img: array,
    dataset: Dataset,
) -> Dataset:
    """
        Read image file from header data and put it into a Dicom Dataset

        Arguments:
        obj - object containing interfile header data
        dataset - Dicom Dataset to save the image data

        Returns:
        dataset - the same dataset that came as an argument but with image metadata
    """

    try:
        if len(binary_img.shape) == 3:
            slices_number = binary_img.shape[0]
            dataset.Columns = binary_img.shape[1]
            dataset.Rows = binary_img.shape[2]
        else:
            dataset.Columns = binary_img.shape[0]
            dataset.Rows = binary_img.shape[1]

        dataset.PixelData = binary_img.tobytes()

        return dataset

    except KeyError as e:
        x = e.args
        LOGGER.error("Missing", x[0], " line from header!")
        raise InterfileDataMissingException

def create_slice_dataset(
    interfile_data: InterfileHeader,
    binary_img: array,
    metadata: Union[CTMetaFile, PETMetaFile],
    slice_number=0,
    number_of_slices=1,
    extended_format: bool=False,
):
    ds = Dataset()
    ds = add_from_interfile_header(obj=interfile_data, dataset=ds)
    ds = add_dicom_metadata(ds)

    ds.StudyDate = datetime.today().strftime("%Y%m%d")

    # Add image to the dataset
    ds = interfile_image_to_dicom_dataset(
        obj=interfile_data,
        binary_img=binary_img,
        dataset=ds
    )

    if metadata:
        ds = add_from_json(obj=metadata, dataset=ds)

    if not extended_format:
        ds = set_slice_position(ds, metadata, slice_number, number_of_slices)

    return ds

def set_slice_position(
        dataset: Dataset,
        metadata: Union[CTMetaFile, PETMetaFile],
        slice_number: int,
        number_of_slices: int
):
    pixel_spacing_x = float(dataset.PixelSpacing[0])
    pixel_spacing_y = float(dataset.PixelSpacing[1])
    pixel_spacing_z = float(dataset.SliceThickness)
    patient_center = metadata.patientCenter

    img_position_patient = [
        -pixel_spacing_x*patient_center[0],
        -pixel_spacing_y*patient_center[1],
        pixel_spacing_z*(slice_number - patient_center[2])
    ]

    setattr(dataset, "ImagePositionPatient", img_position_patient)

    return dataset

def write_dicom(
    interfile_data: InterfileHeader,
    metadata: Union[CTMetaFile, PETMetaFile],
    output_path: Path,
    extended_format: bool
) -> None:
    """
        Writing a dicom file

        Arguments:
        interfile_data - header arguments object
        metadata - additional meta data to add
        output_path - path to save output
        extended_format - should we use extended format (for 3D data)
    """
    binary_img, rescale_slope, rescale_intercept, byte_order_local = read_binary(interfile_data)

    if not extended_format:
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        base_name = output_path.parts[-1]

        # Generate random UUIDs
        SOPInstanceUID = rand_uid()
        SOPClassUID = rand_uid()
        StudyInstanceUID = rand_uid()
        SeriesInstanceUID = rand_uid()
        FrameOfReferenceUID = rand_uid()

        study_time = datetime.today().strftime("%H%M%S.%f")

        number_of_slices = binary_img.shape[0]
        for i in range(number_of_slices):
            img_slice = binary_img[i, :, :].squeeze()
            ds = create_slice_dataset(
                interfile_data=interfile_data,
                binary_img=img_slice,
                metadata=metadata,
                extended_format=extended_format,
                slice_number=i,
                number_of_slices=number_of_slices
            )

            ds.InstanceNumber = str(i+1)
            ds.NumberOfSlices = number_of_slices

            if ds.Modality == "PT":
                ds.ImageIndex = i+1

            ds.RescaleSlope = rescale_slope
            ds.RescaleIntercept = rescale_intercept

            if rescale_slope != 1:
                ds.BitsAllocated = 16
                ds.BitsStored = 16
                ds.HighBit = 15
                ds.PixelRepresentation = 0 # unsigned int
            else:
                ds.BitsAllocated = 8*interfile_data.bytes_per_pixel
                ds.BitsStored = 8*interfile_data.bytes_per_pixel
                ds.HighBit = 8*interfile_data.bytes_per_pixel - 1
                if "unsigned" in interfile_data.number_format:
                    ds.PixelRepresentation = 0 # unsigned int
                else:
                    ds.PixelRepresentation = 1 # signed int

            # Only monochromatic images (one channel per pixel)
            ds.SamplesPerPixel = 1

            ds.StudyDate = datetime.today().strftime("%Y%m%d")
            ds.StudyTime = study_time

            # Assing folder level UUIDs and other data
            ds.SOPInstanceUID = SOPInstanceUID
            ds.SOPClassUID = SOPClassUID
            ds.StudyInstanceUID = StudyInstanceUID
            ds.SeriesInstanceUID = SeriesInstanceUID
            ds.FrameOfReferenceUID = FrameOfReferenceUID

            # TODO: Implement our own Implementation Class UID

            # Set most common options (most common encoding)
            ds.is_little_endian = '<' in byte_order_local
            ds.is_implicit_VR = False

            ds.fix_meta_info()

            # Save file
            ds.save_as(f'{str(output_path)}/{base_name}_{i}.dcm', write_like_original=False)

    # TODO: Fix it!
    else:
        ds = create_slice_dataset(
            interfile_data=interfile_data,
            binary_img=binary_img,
            metadata=metadata,
            extended_format=extended_format,
        )

        # Set most common options (most common encoding)
        ds.is_little_endian = True if '<' in byte_order_local else False
        ds.is_implicit_VR = False

        ds.fix_meta_info()

        # Save file
        ds.save_as(str(output_path), write_like_original=False)

    LOGGER.info('Writing completed!')
