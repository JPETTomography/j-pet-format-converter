#Wrtier module
#Author: Mateusz Kruk
#Version: 2.0
#E-mail: mateusz64.kruk@student.uj.edu.pl

import sys
from pathlib import Path
from typing import Dict
from pydicom.dataset import Dataset
from pydicom.uid import generate_uid

sys.path.insert(1,'..')

from exceptions import *
from settings import *
from reader import read_image

from dicomgenerator.exporter import export
from dicomgenerator.factory import CTDatasetFactory

import factory

def write_uid() -> str:
    return str(generate_uid(
        prefix= UID,
        entropy_srcs=[str(factory.random.randgen.getrandbits(100))] #? trochę nie wiem o co tutaj chodzi
    ))

'''
Writes meta data from header dictionary to dicom dataset.

Arguments:
args - header arguments dictionary
dataset - dicom dataset

Returns:
dataset - dicom dataset with header values
'''

def write_from_header(args: Dict, dataset: Dataset) -> Dataset: #TODO check value formatting
    
    dataset.add_new((0x0010,0x0010),'PN',args["patient name"])
    dataset.add_new((0x008,0x0070),'LO',"NCBJ")

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

'''
Writing a dicom file

Arguments:
args - header arguments dictionary
metadata - additional meta data to add ([NOTE] argument to change)

Returns:
nothing, because it creates a dicom file ([NOTE] can return bool value if needed)
'''

def write_dicom(args: Dict, metadata: Dict) -> None:
    ds = CTDatasetFactory() #take working dataset from dicomgenerator
    ds = write_from_header(args= args, dataset= ds)
    ds = read_image(args= args, dataset= ds) #add to the dataset an image
    export(dataset= ds, path=Path(args["output path"])) #save the file
    print('[INFO] Writing image is complete!')