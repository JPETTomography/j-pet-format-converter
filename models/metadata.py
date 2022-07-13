from pydantic import BaseModel
from typing import Optional


class InterfileHeader(BaseModel):
    modality: str
    data_offset_in_bytes: int
    img_file_name: str
    

class MetaFile(BaseModel):
    Modality: str=''
    Manufacturer: str=''
    StudyTime: str=''
    SeriesTime: str=''
    AcquisitionTime: str=''
    AccessionNumber: str=''
    PatientName: str=''
    PatientID: str
    PatientBirthDate: str=''
    PatientSex: str=''
    PatientAge: Optional[str]
    PatientWeight: Optional[str]
    SliceThickness: str=''
