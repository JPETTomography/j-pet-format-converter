#Wrtier module
#Author: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
import random

from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

from converter.settings import UID
from converter.reader import interfile_image_to_dicom_dataset
from models.metadata import InterfileHeader, MetaFile


LOGGER = logging.getLogger(__name__)


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
    dataset.PatientID = obj.patient.PatientID
    dataset.PatientName = obj.patient.PatientName

    dataset.PatientBirthDate = obj.patient.PatientBirthDate
    dataset.PatientSex = obj.patient.PatientSex

    dataset.PatientAge = obj.patient.PatientAge
    dataset.PatientWeight = obj.patient.PatientWeight

    dataset.Modality = obj.Modality
    dataset.ImageType = obj.ImageType

    dataset.Manufacturer = obj.Manufacturer
    dataset.StudyTime = obj.StudyTime

    dataset.SeriesTime = obj.SeriesTime
    dataset.AcquisitionTime = obj.AcquisitionTime

    dataset.AccessionNumber = obj.AccessionNumber
    dataset.SliceThickness = obj.SliceThickness

    dataset.ImagePositionPatient = obj.ImagePositionPatient
    dataset.ImageOrientationPatient = obj.ImageOrientationPatient

    dataset.SamplesPerPixel = obj.SamplesPerPixel
    dataset.PhotometricInterpretation = obj.PhotometricInterpretation

    dataset.Rows = obj.Rows
    dataset.Columns = obj.Columns
    dataset.PixelSpacing = obj.PixelSpacing
    dataset.BitsAllocated = obj.BitsAllocated
    dataset.BitsStored = obj.BitsStored
    dataset.HighBit = obj.HighBit
    dataset.PixelRepresentation = obj.PixelRepresentation
    dataset.WindowCenter = obj.WindowCenter
    dataset.WindowWidth = obj.WindowWidth
    dataset.RescaleIntercept = obj.RescaleIntercept
    dataset.RescaleSlope = obj.RescaleSlope
    dataset.LossyImageCompression = obj.LossyImageCompression

    return dataset

def init_uuids(dataset: Dataset) -> Dataset:
    # Generate random UUIDs
    dataset.SOPInstanceUID = rand_uid()
    dataset.StudyInstanceUID = rand_uid()
    dataset.SeriesInstanceUID = rand_uid()
    dataset.FrameOfReferenceUID = rand_uid()

    return dataset


def write_dicom(interfile_data: InterfileHeader, metadata: MetaFile, output_path: Path) -> None:
    """
        Writing a dicom file

        Arguments:
        args - header arguments dictionary
        metadata - additional meta data to add

        creates a dicom file
    """
    ds = Dataset()

    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0

    ds = init_uuids(ds)
    ds = add_from_interfile_header(obj=interfile_data, dataset=ds)
    if metadata:
        ds = add_from_json(obj=metadata, dataset=ds)
    ds = interfile_image_to_dicom_dataset(obj=interfile_data, dataset=ds) #add to the dataset an image

    # Set most common options (most common encoding)
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Save file
    ds.save_as(str(output_path))

    LOGGER.info('Writing image is complete!')
