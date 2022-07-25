# Reader module
#Author: Mateusz Kruk, Rafal Mozdzonek

import logging
import sys
import json
from typing import Dict
from pathlib import Path
from numpy.core.records import array
import numpy as np

from converter.exceptions import InterfileInvalidValueException
from converter.exceptions import InterfileInvalidHeaderException
from models.metadata import InterfileHeader, MetaFile


LOGGER = logging.getLogger(__name__)


def recognize_type(bytes_per_pix, is_signed, is_float=False):
    """
    A function to recognize type of the data.
    :param bytes_per_pix: How many bytes are used to encode one pixel. 
    :param is_signed: Are signed other unsigned integers used.
    :param is_float: currently not used
    :return: Numpy type
    """
    if is_signed:
        if bytes_per_pix == 1:
            return np.int8
        elif bytes_per_pix == 2:
            return np.int16
        elif bytes_per_pix== 4:
            return np.int32
        elif bytes_per_pix == 8:
            return np.int64
        else:
            raise ValueError('[ERROR] Invalid type declared!')
    else:
        if bytes_per_pix == 1:
            return np.uint8
        elif bytes_per_pix == 2:
            return np.uint16
        elif bytes_per_pix== 4:
            return np.uint32
        elif bytes_per_pix == 8:
            return np.uint64
        else:
            raise ValueError('[ERROR] Invalid type declared!')


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

            # Get reast of the file
            header = header.readlines()

            for line in header: #line e.g. "!key := value\n"

                # Stripping and splitting line from redundant symbols
                line = line.strip('!\n').split(':=')

                if line != '':

                     # Check if importer encountered "!END OF INTERFILE :="
                    if 'end' in line[0].lower():
                        return meta_dict

                    # Ignore all lines with `general` keyword, usually with empty value
                    elif 'general' not in line[0].lower():

                        try:
                            # Attempt to cast value to int
                            meta_dict[line[0].strip()] = int(line[1])

                        except IndexError:
                            meta_dict[line[0]] = ''

                        # if it's not a number or it's string repesentation of float
                        # then leave it as string
                        except ValueError:

                            meta_dict[line[0].strip()] = line[1].strip()

                        # if something bad happens, throws an exception
                        except Exception as e:
                            raise InterfileInvalidValueException(
                                'invalid header format throws '+ e.__class__.__name__
                            )

        raise InterfileInvalidHeaderException('invalid end header format')

    except FileNotFoundError:
        LOGGER.error("File not found !")
        raise InterfileInvalidHeaderException('header not found')


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

def read_binary(obj: InterfileHeader) -> array:
    """
        Reads image data from a binary file.

        Arguments:
        args - Dictionary containing input parameters.

        Returns:
        - Numpy array containing pixel values.
    """

    byte_order_local = ""

    if "little" in obj.img_byte_order.lower():
      byte_order_local = "little"
    elif "big" in obj.img_byte_order.lower():
      byte_order_local = "big"
    elif "system" in obj.img_byte_order.lower():
      byte_order_local = sys.byteorder
      LOGGER.warn('Byte order was not specified. I will use system\'s default: ' + sys.byteorder)

    values = []
    total_pix = obj.matrix_size_1*obj.matrix_size_2*obj.matrix_size_3
    # Opening the file
    with open(obj.header_file_path + obj.img_file_name, "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // obj.bytes_per_pixel:
        raise IOError(
            'Error: The given image dimensions and encoding does not match given data!'\
            + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
            + '\n\t>\tEstimation from file: '\
            + str(len(byte_list) // obj.bytes_per_pixel)
        )

    for pix_no in range(0, total_pix):
        values.append(
            int.from_bytes(
                byte_list[
                    obj.bytes_per_pixel * pix_no : (obj.bytes_per_pixel * (pix_no + 1))
                ], \
                byteorder=byte_order_local,
                signed="unsigned" not in obj.number_format
            )
    )
    resh_arr = np.asarray(values).reshape(
        (obj.matrix_size_3, obj.matrix_size_2, obj.matrix_size_1)
    )

    return resh_arr


def read_json_meta(path: Path) -> MetaFile:
    """
        Read additional meta data from a JSON file

        Arguments:
        path - Path class containing path to a JSON file

        Returns:
        - dictionary containing meta data
    """
    with open(path, 'r') as f:
        data = json.load(f)
        return MetaFile(**data)
