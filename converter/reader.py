#Reader module
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import sys
from typing import Dict
from PIL import Image
from pathlib import Path
from numpy.core.records import array
from pydicom.dataset import Dataset
import numpy as np

sys.path.insert(1, '..')

from converter.exceptions import *
from converter.settings import CASToR_VERSION
from converter.binary2DICOM import recognize_type

'''
Reads values from Interfile header file

Arguments:
path - Path class containing path to the file 
(absolute path recommended, but will implement conversion from relative path to absolute)

Returns:
meta_dict - dictionary containing all header values
'''


def header_import(path: Path) -> Dict:

  meta_dict = {}

  try:
    with open(path, "r") as header: #opens header file

      meta_dict["header path"] = str(path).strip(path.name) #saves header path for later convenience

      #validation of interfile header (no start flag) 
      if header.readline() != "!INTERFILE := \n": 
        raise InterfileInvalidHeaderException('invalid start header format')

      header = header.readlines()

      for line in header: #line e.g. "!KEY := value\n"

        #stripping and splitting line from redundant symbols
        key, value = line .strip('!\n') .split(' :=')

        if key != '':

          if 'end' in key.lower(): #check if importer encountered "!END OF INTERFILE :="
            return meta_dict

          elif 'general' not in key.lower(): #ignore all keys with general, usually with empty value
            try: #attempt to cast value to int
              meta_dict[key] = int(value) #[NOTE] could cause precision loss if the value was float

            except ValueError: #it's not a number, then cast it as string

              #[NOTE] from my observation sometimes value string has a space before the actual value
              #       what can be annoying to deal with in the further steps
              if value[0] == '':
                meta_dict[key] = value
              else:
                meta_dict[key] = value[1:]

            except Exception as e: #if something bad happens, throws an exception
              raise InterfileInvalidValueException('invalid header format throws '+e.__class__.__name__)

    raise InterfileInvalidHeaderException('invalid end header format')

  except FileNotFoundError:
    print("[ERROR] file not found !")
    raise InterfileInvalidHeaderException('header not found')



'''
Read additional meta data from a JSON file

Arguments:
path - Path class containing path to a JSON file

Returns:
- dictionary containing meta data
'''


def read_json_meta(path: Path) -> Dict:
  pass

'''
Reads image data from a binary file.

[NOTE] THIS METHOD IS COPY-PASTED FROM BINARY2DICOM MODULE

Arguments:
args - Dictionary containing input parameters. 

Returns:
- Numpy array containing pixel values. 
'''


def read_binary(args: Dict) -> array:

    byte_order_local = ""

    if "little" in args['imagedata byte order'].lower():
      byte_order_local = "little"
    elif "big" in args['imagedata byte order'].lower():
      byte_order_local = "big"
    elif "system" in args['imagedata byte order'].lower():
      byte_order_local = sys.byteorder
      print('[WARNING] Byte order was not specified. I will use system\'s default: '+sys.byteorder)

    values = []
    total_pix = args['matrix size [1]']*args['matrix size [2]']*args['matrix size [3]']
    # Opening the file
    with open( args["header path"] + args['name of data file'], "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // args['number of bytes per pixel']:
        raise IOError('[ERROR] The given image dimensions and encoding does not match given data!'\
                      + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
                      + '\n\t>\tEstimation from file: '+str(len(byte_list) // args['number of bytes per pixel']))


    for pix_no in range(0, total_pix):
      values.append(int.from_bytes(byte_list[args['number of bytes per pixel'] * pix_no: (args['number of bytes per pixel'] * (pix_no + 1))], \
                                   byteorder=byte_order_local, signed="unsigned" not in args['number format']))
    resh_arr = np.asarray(values).reshape((args['matrix size [3]'], args['matrix size [2]'], args['matrix size [1]']))

    return resh_arr

'''
Read image file from header data and put it into a Dicom Dataset

Arguments:
args - dictionary containing header data
dataset - Dicom Dataset to save the image data

Returns:
dataset - the same dataset that came as an argument but with image data
'''


def read_image(args: Dict, dataset: Dataset) -> Dataset:

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
    print("[ERROR] missing",x[0]," key from header!")
    raise InterfileDataMissingException
