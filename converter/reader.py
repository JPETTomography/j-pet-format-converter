# Reader module
#Author: Mateusz Kruk, Rafal Mozdzonek

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Union, Tuple

import numpy as np
from numpy.core.records import array

from converter.exceptions import InterfileInvalidHeaderException, InterfileInvalidValueException
from models.metadata import InterfileHeader, CTMetaFile, PETMetaFile

LOGGER = logging.getLogger(__name__)


def _read_interfile_header(path: Path) -> Dict:
    """
        Reads values from Interfile header file

        Arguments:
        path - Path class containing path to the file

        Returns:
        meta_dict - dictionary containing all header values
    """

    meta_dict = {}

    try:
        # Opens header file
        with open(path, "r") as header:

            # Saves header path for later convenience
            meta_dict["header path"] = str(path).replace(path.name, '')

            # Validation of interfile header (no start flag)
            if header.readline() != "!INTERFILE := \n":
                raise InterfileInvalidHeaderException('invalid start header format')

            # Get rest of the file
            header = header.readlines()

            for line in header: #line e.g. "!key := value\n"

                if line.isspace(): continue

                # Stripping and splitting line from redundant symbols
                key, value = line.strip('!\n').split(':=')

                if key != '':

                     # Check if importer encountered "!END OF INTERFILE :="
                    if 'end' in key.lower():
                        return meta_dict

                    # Ignore all lines with `general` keyword, usually with empty value
                    elif 'general' not in key.lower():

                        try:
                            # Attempt to cast value to int
                            meta_dict[key.strip()] = int(value)

                        except IndexError:
                            meta_dict[key.strip()] = ''

                        # if it's not a number or it's string repesentation of float
                        # then leave it as string
                        except ValueError:

                            meta_dict[key.strip()] = value.strip()

                        # if something bad happens, throws an exception
                        except Exception as e:
                            raise InterfileInvalidValueException(
                                'invalid header format throws '+ e.__class__.__name__
                            )

        raise InterfileInvalidHeaderException('invalid end header format')

    except FileNotFoundError:
        LOGGER.error("File not found !")
        raise InterfileInvalidHeaderException(f'header not found: {path}')


def interfile_header_import(path: Path) -> InterfileHeader:
    int_dict = _read_interfile_header(path)
    return InterfileHeader(
        modality=int_dict['imaging modality'],
        keys_version=int_dict['version of keys'],
        castor_version=int_dict['CASToR version'],
        data_offset_in_bytes=int_dict['data offset in bytes'],
        img_file_name=int_dict['name of data file'],
        header_file_path=int_dict['header path'],
        img_byte_order=int_dict['imagedata byte order'],
        images_number=int_dict['total number of images'],
        dimensions_number=int_dict['number of dimensions'],
        matrix_size_1=int_dict['matrix size [1]'],
        matrix_size_2=int_dict['matrix size [2]'],
        matrix_size_3=int_dict['matrix size [3]'],
        number_format=int_dict['number format'],
        bytes_per_pixel=int_dict['number of bytes per pixel'],
        scaling_factor_1=int_dict['scaling factor (mm/pixel) [1]'],
        scaling_factor_2=int_dict['scaling factor (mm/pixel) [2]'],
        scaling_factor_3=int_dict['scaling factor (mm/pixel) [3]'],
        data_rescale_offset=int_dict['data rescale offset'],
        data_rescale_slope=int_dict['data rescale slope'],
        quantification_units=int_dict['quantification units'],
    )

def read_binary(obj: InterfileHeader) -> Tuple[array, float, float, str]:
    """
        Reads image data from a binary file.

        Arguments:
        args - Dictionary containing input parameters.

        Returns:
        - Numpy array containing pixel values.
    """

    byte_order_local = ""

    if "little" in obj.img_byte_order.lower():
        byte_order_local = "<"
    elif "big" in obj.img_byte_order.lower():
        byte_order_local = ">"
    elif "system" in obj.img_byte_order.lower():
        byte_order_local = '<' if sys.byteorder == 'little' else '>'
        LOGGER.warning(
            'Byte order was not specified. I will use system\'s default: %s' % sys.byteorder
        )

    if 'float' in obj.number_format:
        ttype = 'f'
    elif 'short' in obj.number_format:
        assert obj.bytes_per_pixel == 2
        ttype = 'f'
    elif 'long' in obj.number_format:
        assert obj.bytes_per_pixel == 8
        ttype = 'f'
    elif "unsigned" in obj.number_format:
        ttype = 'u'
    elif "signed" in obj.number_format:
        ttype = 'i'
    else:
        raise(Exception(f"Unsupported data format: {obj.number_format}"))

    data_type = byte_order_local + ttype + str(obj.bytes_per_pixel)

    image_matrix = np.fromfile(obj.header_file_path + obj.img_file_name, dtype=data_type, count=-1)
    resh_arr = image_matrix.reshape((obj.matrix_size_3, obj.matrix_size_2, obj.matrix_size_1))
    # TODO: Understand why it is needed here
    # Flip every slice of 3D image (Y and Z axes) to match reference test case.
    resh_arr = resh_arr[::-1, ::-1, :]

    rescale_intercept = 0
    rescale_slope = 1

    if 'float' in obj.number_format:
        rescale_intercept = resh_arr.min()
        rescale_slope = (resh_arr.max() - resh_arr.min())/np.iinfo(np.int16).max
        resh_arr = (resh_arr - rescale_intercept)/rescale_slope

        resh_arr = resh_arr.astype(np.uint16)

    return resh_arr, rescale_slope, rescale_intercept, byte_order_local


def read_json_meta(path: Path, file_type: str) -> Union[CTMetaFile, PETMetaFile]:
    """
        Read additional meta data from a JSON file

        Arguments:
        path - Path class containing path to a JSON file

        Returns:
        - dictionary containing meta data
    """
    with open(path, 'r') as f:
        data = json.load(f)
        if file_type == "CT":
            return CTMetaFile(**data)
        return PETMetaFile(**data)
