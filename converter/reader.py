#Reader module
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import sys
from typing import Dict
from PIL import Image
from pathlib import Path
from pydicom.dataset import Dataset
import numpy as np

sys.path.insert(1, '..')

from converter.exceptions import *
from converter.settings import CASToR_VERSION
from converter.binary2DICOM import recognize_type
from converter.interfile2DICOM import parseHead
'''
Reads values from Interfile header file

Arguemnts:
path - Path class containing path to the file 
(absolute path recomended, but will implement conversion from relative path to absolute)

Returns:
meta_dict - dictionary containg all header values
'''


def header_import(path: Path):

  meta_dict = {}

  try:
    with open(path, "r") as header:

      meta_dict["header path"] = str(path).strip(path.name)

      line = header.readline()
      if line != "!INTERFILE := \n":
        raise InterfileInvalidHeaderException('invalid start header format')

      bufor = header.readlines()

      for line in bufor:
        line = line.strip('!\n')
        line = line.split(' :=')
        if line[0] != '':
          if 'end' in line[0].lower():
            return meta_dict
          elif 'general' not in line[0].lower():
            try:
              meta_dict[line[0]] = int(line[1])
            except ValueError:
              if line[1][0] == '':
                meta_dict[line[0]] = line[1]
              else:
                meta_dict[line[0]] = line[1][1:]
            except Exception:
              raise InterfileInvalidValueException('invalid header format')

    raise InterfileInvalidHeaderException('invalid end header format')

  except FileNotFoundError:
    print("[ERROR] file not found !")
    raise InterfileInvalidHeaderException

  except Exception as e:
    x = e.args
    print("[ERROR]", x[0], "!")
    raise e


'''
Read additional meta data from a JSON file

Arguments:
path - Path class containg path to a JSON file

Returns:
- dictionary conatining meta data
'''


def read_json_meta(path: Path):
  pass


def read_binary(args: Dict):
    """
    Reads image data from a binary file.
    :param arguments: Dictionary containing input parameters. 
    :return: Numpy array containing pixel values. 
    """

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
    with open(args['name of data file'], "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // args['number of bytes per pixel']:
        raise IOError('[ERROR] The given image dimensions and encoding does not match given data!'\
                      + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
                      + '\n\t>\tEstimation from file: '+str(len(byte_list) // args['number of bytes per pixel']))


    for pix_no in range(0, total_pix):
      values.append(int.from_bytes(byte_list[args['number of bytes per pixel'] * pix_no: (args['number of bytes per pixel'] * (pix_no + 1))], \
                                   byteorder=byte_order_local, signed="unsigned" not in args['number format']))
    resh_arr = np.asarray(values).reshape((args['matrix size [3]'], args['matrix size [2]'], args['matrix size [1]']))
    print('[INFO] Reading image data is complete!')
    return resh_arr

'''
Read image file from header data and put it into a Dicom Dataset

Arguments:
args - dictionary containing header data
dataset - Dicom Dataset to save the image data

Returns:
dataset - the same dataset that came as an argument but with image data
'''


def read_image(args: Dict, dataset: Dataset):

  try:
    args["name of data file"] = "../examples/" + args["name of data file"]
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
