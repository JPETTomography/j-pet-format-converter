class I2DException(Exception):
    '''Base Interfile to Dicom exception'''
    pass

class InterfileInvalidHeaderException(I2DException):
    '''Interfile header file is invalid'''
    pass

class InterfileInvalidValueException(I2DException):
    '''Exception for invalid value imported from Interfile'''
    pass

class InterfileDataMissingException(I2DException):
    '''Mandatory value missing from Interfile'''
    pass
