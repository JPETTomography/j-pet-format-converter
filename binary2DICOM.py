#!/usr/bin/env python3
# binary2DICOM converter
# Author: Rafal Maselek
# Email: rafal.maselek@ncbj.gov.pl
#
# This script enables converting raw 3D binary images to DICOM file format and importing meta-data from external file.

import sys
try:
  from pydicom.dataset import Dataset, FileDataset
except ImportError:
  from dicom.dataset import Dataset, FileDataset

import datetime
import time
import argparse
import numpy as np
binary2DICOM_version = "version 1.3 features included:\n\t1)Reading raw binary file with image\n\t2)Reading file with meta-data\n\t3)Creating\
 a new DICOM file\n\t4)Reading image parameters from meta-data\n\t5)Smart argument parser\n\t6)Using converter as a module"


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


def read_meta(filename):
    """
    A naive parser for DICOM meta-data.
    :param filename: Contains meta-data in a format: <group tag> , <element tag> , <VR>, <value> Commas are delimiters.
    :return: An array N x 3, where N is the number of correctly parsed lines.
    """
    meta_arr = []
    lines_with_data = 0
    with open(filename) as f:
        for line_no, line in enumerate(f):
            line = line.partition('#')[0]
            line = line.strip()
            line = line.split(',')
            err_str = ' could not be parsed correctly!'
            if len(line[0]) > 0:
                lines_with_data +=1
                if len(line) > 4:
                    print("[WARNING] Line "+str(line_no+1)+" contains more values than required. Please, check it.")
                try:
                    if len(str(line[2]).strip()) != 2:
                        raise ValueError('VR should consist of exactly 2 characters! VR parsed:'+str(line[2]).strip())
                    line_data = [int(line[0], 16), int(line[1], 16), str(line[2]).strip()]
                    # parsing the value
                    val = line[3].strip()
                    if val[0] == '\'' or val[-1] == '\'':
                        # parse as string
                        line_data.append(val.replace('\'', '').strip())
                    elif val.find('.') != -1:
                        # parse as float
                        line_data.append(float(val))
                    else:
                        # parse as int
                        line_data.append(int(val))
                    meta_arr.append(line_data)

                except ValueError as e:
                    print('[WARNING] Line '+str(line_no+1)+err_str + " Wrong value!" + "ERR MSG: "+str(e))
                except IndexError as e:
                    print('[WARNING] Line '+str(line_no+1)+err_str + " Tags or/and value are missing!" + "ERR MSG: "+str(e))
    print("[INFO] Reading meta-data is complete! " + str(len(meta_arr))+'/'+str(lines_with_data)+' lines were parsed correctly.')
    return meta_arr


def write_meta(meta_data, data_set):
    """
    Writes meta data into the data set.
    :param meta_data: Array N x 4, where N is the number of data elements.
    :param data_set: Dicom Data Set
    :return: Modified  Data Set 
    """
    for elem in meta_data:
        data_set.add_new((hex(elem[0]), hex(elem[1])), elem[2], elem[3])
    return data_set


def read_binary(arguments):
    """
    Reads image data from a binary file.
    :param arguments: Dictionary containing input parameters. 
    :return: Numpy array containing pixel values. 
    """
    if arguments['byte_order'] == 'system':
        byte_order_local = sys.byteorder
        print('[WARNING] Byte order was not specified. I will use system\'s default: '+sys.byteorder)
    else:
        byte_order_local = arguments['byte_order']
    values = []
    total_pix = arguments['width']*arguments['height']*arguments['frames']
    # Opening the file
    with open(arguments['in_file'], "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // arguments['bytes_per_pix']:
        raise IOError('[ERROR] The given image dimensions and encoding does not match given data!'\
                      + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
                      + '\n\t>\tEstimation from file: '+str(len(byte_list) // arguments['bytes_per_pix']))

    # decoding depends on whether data is float or not
    if arguments['is_float']:
        raise ValueError('[ERROR] Floats are currently unavailable!')
        # TODO: enable reading floats
        # for pix_no in range(0, total_pix):
        #     values.append(float.from_bytes(byte_list[bytes_per_pix * pix_no: (bytes_per_pix * (pix_no + 1))], \
        #                                  byteorder=byte_order_local, signed=is_signed))
    else:
        for pix_no in range(0, total_pix):
            values.append(int.from_bytes(byte_list[arguments['bytes_per_pix'] * pix_no: (arguments['bytes_per_pix'] * (pix_no + 1))], \
                                           byteorder=byte_order_local, signed=arguments['is_signed']))
    resh_arr = np.asarray(values).reshape((arguments['frames'], arguments['width'], arguments['height']))
    print('[INFO] Reading image data is complete!')
    return resh_arr


def write_dicom(arguments, pixel_array, meta_arr = []):
    """
    Function to create completely new DICOM file.
    :param arguments: Dictionary containing input parameters.
    :param pixel_array: 2D or 3D numpy array containing pixel values.
    :param meta_arr: An array contaning parsed meta data.
    :return: 
    """
    #TODO:Check the possibility to use UID generator instead hardcoded ones.

    file_meta = Dataset()
    # The Secondary Capture (SC) Image Information Object Definition (IOD) specifies images that are converted from
    # a non-DICOM format to a modality independent DICOM format.
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = '1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780'
    file_meta.ImplementationClassUID = '1.3.6.1.4.1.9590.100.1.0.100.4.0'
    # Since we don't want to store any additional info in the header, we set it to x00
    ds = FileDataset(arguments['out_file'], {}, file_meta=file_meta, preamble=b'0' * 128)

    # Type of equipment that originally acquired the data.
    ds.Modality = 'WSD'

    # Setting the date and time
    ds.ContentDate = str(datetime.date.today()).replace('-', '')
    ds.ContentTime = str(time.time())  # milliseconds since the epoch

    # Keep scrolling :)
    ds.SOPClassUID = 'Secondary Capture Image Storage'
    ds.SOPInstanceUID = '1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780'
    ds.StudyInstanceUID = '1.3.6.1.4.1.9590.100.1.1.124313977412360175234271287472804872093'
    ds.SeriesInstanceUID = '1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143649'

    # Manufacturer
    ds.SecondaryCaptureDeviceManufctur = 'NCBJ'

    # These are the necessary imaging components of the FileDataset object.

    # Number of color channels.
    ds.SamplesPerPixel = 1
    # It defines what does every color channel hold
    ds.PhotometricInterpretation = "MONOCHROME2"
    #
    ds.PixelRepresentation = 0
    ds.HighBit = 15

    # Here meta-data is put into the Data Set. It can override hardcoded values, but parameters providided as program
    # arguments will be inserted no matter what is in the meta-data file.
    ds = write_meta(meta_arr, ds)

    # How many bits are allocated to store pixel info
    ds.BitsAllocated = arguments['bytes_per_pix'] * 8
    # How many bits are used to store pixel info
    ds.BitsStored = arguments['bytes_per_pix']*8
    # Whether signed or unsigned numbers are used
    if arguments['is_signed']:
        ds.PixelRepresentation = 1
    else:
        ds.PixelRepresentation = 0

    # Read from data the dimensions.
    if len(pixel_array.shape) == 3:
        ds.NumberOfFrames = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]
        ds.Rows = pixel_array.shape[2]
    else:
        ds.Columns = pixel_array.shape[0]
        ds.Rows = pixel_array.shape[1]

    try:
        err_str = '[ERROR] The file could not be created because of: '

        data_type = recognize_type(arguments['bytes_per_pix'], arguments['is_signed'], arguments['is_float'])
        if pixel_array.dtype != data_type:
            pixel_array = pixel_array.astype(data_type)
        ds.PixelData = pixel_array.tostring()

        ds.save_as(arguments['out_file'].replace('.dcm', '') + '.dcm')
        print('[INFO] Writing to DICOM file is complete!')
    except ValueError as ve:
        print(err_str+'ValueError '+str(ve))
        sys.exit(1)
    except FileExistsError as fe:
        print(err_str+'FileExistsError '+str(fe))
        sys.exit(1)
    except Exception as e:
        print(err_str+str(e))
        sys.exit(1)


def convert(arguments):
    """
    Calls functions to read binary image and write it (with meta data) to a new DICOM file.
    :param arguments: Dictionary containing input parameters. 
    {'meta': <META DATA FILE, STRING>, 'in_file': <INPUT FILE, STRING>, 'out_file': <OUTPUT FILE, STRING>,
    'width': <INT>, 'height': <INT>, 'frames': <INT>,
    'is_signed': <BOOL>,  'byte_order': <'little' OR 'big'>,  'bytes_per_pix': <INT>,  'is_float': <BOOL>}
    :return: 
    """
    meta_arr = []
    try:
        if arguments['meta'] != '':
            meta_arr = read_meta(arguments['meta'])
    except FileNotFoundError as fnfe:
        print("[ERROR] Meta-data was not loaded, because the file was not found: "+str(fnfe))
        sys.exit(1)
    image_arr = read_binary(arguments)
    write_dicom(arguments, image_arr, meta_arr)


def main():
    """
    Main function of the program, parses the input parameters and calls necessary functions.
    :return: 
    """
    parser = argparse.ArgumentParser(
        description='This is a binary -> DICOM converter created by Rafal Maselek.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', metavar='input_file_name', type=str)
    parser.add_argument('out_file', metavar='output_file_name', type=str)
    parser.add_argument('width', metavar='image_width', type=int)
    parser.add_argument('height', metavar='image_height', type=int)
    parser.add_argument('frames', metavar='no._of_frames', type=int)
    parser.add_argument('-bpp', '--bytes_per_pix', metavar='bytes_per_pixel', type=int, nargs='?', default=2, help='Pixel encoding')
    parser.add_argument('-uint', '--unsigned', dest='is_signed', action='store_false', help='Use unsigned ints', default=False)
    parser.add_argument('-int', '--signed', dest='is_signed', action='store_true', help='Use signed ints', default=True)
    parser.add_argument('-f', '--float', dest='is_float', action='store_true', help='Not supported now', default=False)
    parser.add_argument('-nf', '--non_float', dest='is_float', action='store_false', help='Not supported now')
    parser.add_argument('-bo', '--byte_order', metavar='byte_order', type=str, nargs='?', default='system', choices=['little', 'big'],\
                        help='ENDIAN type (little/big)')
    parser.add_argument('-m', '--meta', help='use external meta data', type=str, nargs='?', default='')
    parser.add_argument('-v', '--version', action='version', version=binary2DICOM_version)

    try:
        args = parser.parse_args()
        args_dict = vars(args)
        if args_dict['width'] < 1:
            raise ValueError('Invalid value of image width! It has to be >0')
        if args_dict['height'] < 1:
            raise ValueError('Invalid value of image height! It has to be >0')
        if args_dict['bytes_per_pix'] < 1:
            raise ValueError('Invalid number of bytes_per_pixel! It has to be >0')

    except ValueError as ve:
        print('[ERROR] Could not parse input parameters correctly! ' +str(ve))
        exit(1)
    except Exception as e:
        print('[ERROR] Unknown error! Could not parse input parameters correctly! ' + str(e))
        exit(1)
    print('[INFO] Parsed arguments:')
    print(args_dict)
    convert(args_dict)


if __name__ == "__main__":
    main()





