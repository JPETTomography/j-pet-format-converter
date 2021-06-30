#Wrtier module
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import sys
from pathlib import Path
from typing import Dict
from pydicom.dataset import Dataset

sys.path.insert(1,'..')

from converter.exceptions import *
from converter.settings import TEST_DIR
from converter.reader import read_image

from dicomgenerator.exporter import export
from dicomgenerator.factory import CTDatasetFactory

def write_to_dataset(data: Dict, dataset: Dataset):
    if len(data) > 0:
        for value in data:
            pass
    else:
        raise ValueError

def write_dicom(args: Dict, metadata: Dict):
    ds = CTDatasetFactory()
    ds = read_image(args= args, dataset= ds)
    name = "/" + args["patient name"] + ".dcm"
    export(dataset= ds, path=Path(args["header path"]+name))