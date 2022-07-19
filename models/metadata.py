from pydantic import BaseModel
from typing import Optional, List


class InterfileHeader(BaseModel):
    modality: str
    keys_version: str
    castor_version: str
    data_offset_in_bytes: int
    img_file_name: str
    header_file_path: str
    img_byte_order: str
    images_number: int
    dimensions_number: int
    matrix_size_1: int
    matrix_size_2: int
    matrix_size_3: int
    number_format: str
    bytes_per_pixel: int
    scaling_factor_1: str
    scaling_factor_2: str
    scaling_factor_3: str
    data_rescale_offset: int
    data_rescale_slope: int
    quantification_units: int

class PatientData(BaseModel):
    PatientID: str
    PatientName: str=''
    PatientBirthDate: str=''
    PatientSex: str=''
    PatientAge: Optional[str]
    PatientWeight: Optional[str]

class MetaFile(BaseModel):
    patient: PatientData

    Modality: str='PT'

    ImageType: List[str]

    Manufacturer: str=''
    StudyTime: str=''
    SeriesTime: str=''
    AcquisitionTime: str=''
    AccessionNumber: str=''
    SliceThickness: str=''

    ImagePositionPatient: List[float]
    ImageOrientationPatient: List[int]

    SamplesPerPixel: int
    PhotometricInterpretation: str
    Rows: int
    Columns: int
    PixelSpacing: List[float]
    BitsAllocated: int
    BitsStored: int
    HighBit: int
    PixelRepresentation: int
    WindowCenter: List[int]
    WindowWidth: List[int]
    RescaleIntercept: str
    RescaleSlope: str
    LossyImageCompression: str
