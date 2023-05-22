from typing import List, Tuple, Optional, Union, Literal

from pydantic import BaseModel


class InterfileHeader(BaseModel):
    modality: Literal['CT', 'PT']
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

class BaseMetaData(BaseModel):
    @classmethod
    def get_field_names(cls,alias=False):
        props = cls.schema(alias).get("properties")
        return list(props.keys()) if props else []

    def __getitem__(self, item):
        return getattr(self, item)

class PatientData(BaseMetaData):
    PatientID: str
    PatientName: str=''
    PatientBirthDate: str=''
    PatientSex: str=''
    PatientAge: Optional[str]
    PatientWeight: Optional[str]
    PatientPosition: str

class CTMetaFile(BaseMetaData):
    patient: PatientData
    patientCenter: Tuple[int, int, int]

    ImageOrientationPatient: Tuple[float, float, float, float, float, float]

    ImageType: Tuple[Literal['ORIGINAL', 'DERIVED'], Literal['PRIMARY', 'SECONDARY']]

    Manufacturer: str=''
    StudyTime: Optional[str]
    SeriesTime: Optional[str]
    AcquisitionTime: Optional[str]
    AccessionNumber: Optional[str]

    PhotometricInterpretation: Literal["MONOCHROME1", "MONOCHROME2"]
    WindowCenter: Union[List[int], str]
    WindowWidth: Union[List[int], str]
    LossyImageCompression: Optional[str]

class PetSeries(BaseMetaData):
    SeriesDescription: Optional[str]
    SeriesDate: str
    SeriesTime: str
    CollimatorType: Literal['NONE', 'RING']
    CorrectedImage: List[Literal['DECY', 'ATTN', 'SCAT', 'DTIM', 'MOTN', 'PMOT', 'CLN', 'RAN', 'RADL', 'DCAL', 'NORM', 'BEDR']]
    SeriesType: Tuple[Literal['STATIC', 'DYNAMIC', 'GATED', 'WHOLE BODY'], Literal['IMAGE', 'REPROJECTION']]
    Units: Literal['CNTS', 'NONE', 'CM2', 'CM2ML', 'PCNT', 'CPS', 'BQML', 'MGMINML', 'UMOLMINML', 'MLMING', 'MLG', '1CM', 'UMOLML', 'PROPCNTS', 'PROPCPS', 'MLMINML', 'MLML', 'GML', 'STDDEV']
    CountsSource: Literal['EMISSION', 'TRANSMISSION']
    DecayCorrection: Literal['NONE', 'START', 'ADMIN']

class RadionuclideCode(BaseMetaData):
    CodeValue: str
    CodingSchemeDesignator: str
    CodeMeaning: str
    MappingResource: str
    ContextGroupVersion: str

class RadionuclideInformation(BaseMetaData):
    RadionuclideCodeSequence: List[RadionuclideCode]

class PETIsotope(BaseMetaData):
    RadiopharmaceuticalInformationSequence: List[RadionuclideInformation]

class PatientOrientationModifierCode(BaseMetaData):
    CodeValue: str
    CodingSchemeDesignator: str
    CodeMeaning: str
    MappingResource: str
    ContextGroupVersion: str

class PatientOrientationCode(BaseMetaData):
    CodeValue: str
    CodingSchemeDesignator: str
    CodeMeaning: str
    MappingResource: str
    ContextGroupVersion: str
    PatientOrientationModifierCodeSequence: List[Optional[PatientOrientationModifierCode]]

class PatientGantryRelationshipCode(BaseMetaData):
    CodeValue: str
    CodingSchemeDesignator: str
    CodeMeaning: str
    MappingResource: str
    ContextGroupVersion: str

class PatientOrientation(BaseMetaData):
    PatientOrientationCodeSequence: List[Optional[PatientOrientationCode]]
    PatientGantryRelationshipCodeSequence: List[Optional[PatientGantryRelationshipCode]]

class PETMetaFile(BaseMetaData):
    patient: PatientData
    petSeries: PetSeries
    petIsotope: PETIsotope
    petPatientOrientation: PatientOrientation
    patientCenter: Tuple[int, int, int]

    ImageOrientationPatient: Tuple[float, float, float, float, float, float]

    ImageType: Tuple[Literal['ORIGINAL', 'DERIVED'], Literal['PRIMARY', 'SECONDARY']]
    FrameReferenceTime: str
    DecayFactor: str

    Manufacturer: str=''
    StudyTime: Optional[str]
    SeriesTime: Optional[str]
    AcquisitionTime: Optional[str]
    AccessionNumber: Optional[str]

    PhotometricInterpretation: Literal["MONOCHROME1", "MONOCHROME2"]
    WindowCenter: Union[List[int], str]
    WindowWidth: Union[List[int], str]
    LossyImageCompression: Optional[str]

    StudyDescription: str
