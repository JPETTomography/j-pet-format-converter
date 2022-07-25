# Wrtier module
#Author: Mateusz Kruk, Rafal Mozdzonek

import os
import logging
from pathlib import Path
import random

from numpy.core.records import array
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

from converter.settings import UID
from converter.exceptions import InterfileDataMissingException
from converter.reader import read_binary, recognize_type
from models.metadata import InterfileHeader, MetaFile, PatientData


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


def rand_uid() -> str:
    return str(generate_uid(
        prefix= UID,
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

    return dataset

def add_from_json(obj: MetaFile, dataset: Dataset) -> Dataset:
    """
        Writes json meta data to dicom dataset.

        Arguments:
        obj - MetaFile object
        dataset - dicom dataset

        Returns:
        dataset - dicom dataset with inserted values
    """
    tags = MetaFile.get_field_names()
    tags = filter(lambda k: k[0].isupper(), tags)

    for tag in tags:
        setattr(dataset, tag, obj[tag])

    patient_tags = PatientData.get_field_names()
    patient_tags = filter(lambda k: k[0].isupper(), patient_tags)

    for patient_tag in patient_tags:
        setattr(dataset, patient_tag, obj.patient[patient_tag])

    return dataset

def init_uuids(dataset: Dataset) -> Dataset:
    # Generate random UUIDs
    dataset.SOPInstanceUID = rand_uid()
    dataset.StudyInstanceUID = rand_uid()
    dataset.SeriesInstanceUID = rand_uid()
    dataset.FrameOfReferenceUID = rand_uid()

    return dataset


def interfile_image_to_dicom_dataset(
    obj: InterfileHeader,
    binary_img: array,
    dataset: Dataset
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

        dataset.PixelData = binary_img.astype(
            recognize_type(obj.bytes_per_pixel, True)
        ).tobytes()

        return dataset

    except KeyError as e:
        x = e.args
        LOGGER.error("Missing", x[0], " line from header!")
        raise InterfileDataMissingException

def create_slice_dataset(
    interfile_data: InterfileHeader,
    binary_img: array,
    metadata: MetaFile,
    extended_format: bool
):
    ds = Dataset()
    ds = init_uuids(ds)
    ds = add_from_interfile_header(obj=interfile_data, dataset=ds)

    # Add image to the dataset
    ds = interfile_image_to_dicom_dataset(
        obj=interfile_data,
        binary_img=binary_img,
        dataset=ds
    )

    if metadata:
        ds = add_from_json(obj=metadata, dataset=ds)

    return ds

def write_dicom(
    interfile_data: InterfileHeader,
    metadata: MetaFile,
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

        creates a dicom file
    """
    binary_img = read_binary(interfile_data)

    if not extended_format:
        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        base_name = output_path.parts[-1]

        slices_number = binary_img.shape[0]
        for i in range(slices_number):
            img_slice = binary_img[i, :, :].squeeze()
            ds = create_slice_dataset(
                interfile_data=interfile_data,
                binary_img=img_slice,
                metadata=metadata,
                extended_format=extended_format
            )

            # Set most common options (most common encoding)
            ds.is_little_endian = True
            ds.is_implicit_VR = False

            # Save file
            ds.save_as(f'{str(output_path)}/{base_name}_{i}.dcm')
    else:
        ds = create_slice_dataset(
            interfile_data=interfile_data,
            binary_img=binary_img,
            metadata=metadata,
            extended_format=extended_format
        )

        # Set most common options (most common encoding)
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        # Save file
        ds.save_as(str(output_path))

    LOGGER.info('Writing image is complete!')
