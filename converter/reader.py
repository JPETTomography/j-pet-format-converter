#Reader module
#Author: Mateusz Kruk, Rafal Mozdzonek

import logging
import sys
from typing import Dict
from pathlib import Path
from numpy.core.records import array
from pydicom.dataset import Dataset
import numpy as np

from converter.exceptions import InterfileDataMissingException, InterfileInvalidValueException
from converter.exceptions import InterfileInvalidHeaderException
from  converter.binary2DICOM import recognize_type
from models.metadata import InterfileHeader


LOGGER = logging.getLogger(__name__)


def interfile_header_import(path: Path) -> Dict:
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
                            meta_dict[line[0]] = int(line[1])

                        except IndexError:
                            meta_dict[line[0]] = ''

                        # if it's not a number or it's string repesentation of float
                        # then leave it as string
                        except ValueError:

                            meta_dict[line[0]] = line[1].strip()

                        except Exception as e: #if something bad happens, throws an exception
                            raise InterfileInvalidValueException(
                                'invalid header format throws '+ e.__class__.__name__
                            )

        raise InterfileInvalidHeaderException('invalid end header format')

    except FileNotFoundError:
        LOGGER.error("File not found !")
        raise InterfileInvalidHeaderException('header not found')


def read_binary(args: Dict) -> array:
    """
        Reads image data from a binary file.

        Arguments:
        args - Dictionary containing input parameters.

        Returns:
        - Numpy array containing pixel values.
    """

    byte_order_local = ""

    if "little" in args['imagedata byte order'].lower():
      byte_order_local = "little"
    elif "big" in args['imagedata byte order'].lower():
      byte_order_local = "big"
    elif "system" in args['imagedata byte order'].lower():
      byte_order_local = sys.byteorder
      LOGGER.warn('Byte order was not specified. I will use system\'s default: ' + sys.byteorder)

    values = []
    total_pix = args['matrix size [1]']*args['matrix size [2]']*args['matrix size [3]']
    # Opening the file
    with open(args["header path"] + args['name of data file'], "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // args['number of bytes per pixel']:
        raise IOError(
            'Error: The given image dimensions and encoding does not match given data!'\
            + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
            + '\n\t>\tEstimation from file: '\
            + str(len(byte_list) // args['number of bytes per pixel'])
        )

    for pix_no in range(0, total_pix):
        values.append(
            int.from_bytes(
                byte_list[
                    args['number of bytes per pixel'] * pix_no : (args['number of bytes per pixel'] * (pix_no + 1))
                ], \
                byteorder=byte_order_local,
                signed="unsigned" not in args['number format']
            )
    )
    resh_arr = np.asarray(values).reshape(
        (args['matrix size [3]'], args['matrix size [2]'], args['matrix size [1]'])
    )

    return resh_arr


def interfile_image_to_dicom_dataset(obj: InterfileHeader, dataset: Dataset) -> Dataset:
    """
        Read image file from header data and put it into a Dicom Dataset

        Arguments:
        args - dictionary containing header data
        dataset - Dicom Dataset to save the image data

        Returns:
        dataset - the same dataset that came as an argument but with image data
    """

    try:
        pix_np = read_binary(args)
        dataset.PixelData = pix_np.astype(
            recognize_type(args['number of bytes per pixel'], True)
        ).tobytes()

        if len(pix_np.shape) == 3:
            dataset.NumberOfFrames = pix_np.shape[0]
            dataset.Columns = pix_np.shape[1]
            dataset.Rows = pix_np.shape[2]
        else:
            dataset.Columns = pix_np.shape[0]
            dataset.Rows = pix_np.shape[1]

        return dataset

    except KeyError as e:
        x = e.args
        LOGGER.error("Missing", x[0], " line from header!")
        raise InterfileDataMissingException


def read_json_meta(path: Path) -> Dict:
    """
        Read additional meta data from a JSON file

        Arguments:
        path - Path class containing path to a JSON file

        Returns:
        - dictionary containing meta data
    """
    pass
