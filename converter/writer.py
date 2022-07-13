#Wrtier module
#Author: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
from typing import Dict

import factory
import pydicom
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

from converter.settings import *
from converter.reader import interfile_image_to_dicom_dataset
from models.metadata import InterfileHeader, MetaFile


LOGGER = logging.getLogger(__name__)

def init_dicom_dataset():
    ds = Dataset()


def write_uid() -> str:
    return str(generate_uid(
        prefix= UID,
        entropy_srcs=[str(factory.random.randgen.getrandbits(100))]
    ))


def write_from_interfile_header(obj: InterfileHeader, dataset: Dataset) -> Dataset:
    """
        Writes interfile meta data from header dictionary to dicom dataset.

        Arguments:
        obj - InterfileHeader obj
        dataset - dicom dataset

        Returns:
        dataset - dicom dataset with inserted header values
    """

    return dataset

def write_from_json(obj: MetaFile, dataset: Dataset) -> Dataset:
    """
        Writes json meta data to dicom dataset.

        Arguments:
        obj - MetaFile object
        dataset - dicom dataset

        Returns:
        dataset - dicom dataset with inserted values
    """
    dataset.patientName = obj.PatientName
    dataset.PatientID = obj.PatientID

    return dataset

def init_uuids(dataset: Dataset) -> Dataset:
    # Generate random UUIDs
    dataset.SOPInstanceUID = write_uid()
    dataset.StudyInstanceUID = write_uid()
    dataset.SeriesInstanceUID = write_uid()
    dataset.FrameOfReferenceUID = write_uid()

    return dataset

#prototype for writing from JSON to dataset

def write_to_dataset(data: Dict, dataset: Dataset) -> None:
    if len(data) > 0:
        for value in data:
            pass
    else:
        raise ValueError

def write_dicom(interfile_data: Dict, metadata: Dict) -> None:
    """
        Writing a dicom file

        Arguments:
        args - header arguments dictionary
        metadata - additional meta data to add

        creates a dicom file
    """
    interfile_header = InterfileHeader(interfile_data)

    ds = Dataset()
    ds = init_uuids(ds)
    ds = write_from_interfile_header(obj=interfile_header, dataset=ds)
    ds = write_from_json(obj=MetaFile(interfile_data), dataset=ds)
    ds = interfile_image_to_dicom_dataset(obj=interfile_header, dataset=ds) #add to the dataset an image

    # set most common options (most common encoding)
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Save file
    ds.save_as(str(Path(args["outputPath"])))

    LOGGER.info('Writing image is complete!')
