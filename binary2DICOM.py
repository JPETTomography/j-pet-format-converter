# Author: Rafal Maselek
# Email: rafal.maselek@ncbj.gov.pl
#
# This script enables converting raw 3D binary images to DICOM file format.

import sys
from dicom.dataset import Dataset, FileDataset
import numpy as np
import datetime, time


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
            raise ValueError('Invalid type declared!')
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
            raise ValueError('Invalid type declared!')


def read_header(filename):
    pass


def read_binary(filename, width, height, frames, bytes_per_pix=2, is_signed=False, is_float=False, byte_order=''):
    """
    :param filename: Name of the file to be read.
    :param width: The width dimension of images.
    :param height: The height dimension of images.
    :param frames: Number of images.
    :param bytes_per_pix: How many bytes are used to encode one pixel.
    :param is_signed: Are signed or unsigned types used to encode image.
    :param is_float: currently not used
    :param byte_order: 'big' or 'little', when empty the default for the machine will be used    
    :return: Numpy array containing pixel values. 
    """
    if byte_order == '':
        byte_order_local = sys.byteorder
    else:
        byte_order_local = byte_order
    values = []
    total_pix = width*height*frames
    # Opening the file
    with open(filename, "rb") as f:
        byte_list = f.read()
    if total_pix != len(byte_list) // bytes_per_pix:
        raise IOError('The given image dimensions and encoding does not match given data!'\
                      + '\n\t>\tTotal number of pixels declared: '+str(total_pix)\
                      + '\n\t>\tEstimation from file: '+str(len(byte_list) // bytes_per_pix))

    # decoding depends on whether data is float or not
    if is_float:
        pass
        # for pix_no in range(0, total_pix):
        #     values.append(float.from_bytes(byte_list[bytes_per_pix * pix_no: (bytes_per_pix * (pix_no + 1))], \
        #                                  byteorder=byte_order_local, signed=is_signed))
    else:
        for pix_no in range(0, total_pix):
            values.append(int.from_bytes(byte_list[bytes_per_pix * pix_no: (bytes_per_pix * (pix_no + 1))], \
                                           byteorder=byte_order_local, signed=is_signed))
    resh_arr = np.asarray(values).reshape((frames, width, height))
    print('Reading complete!')
    return resh_arr


def write_dicom(filename, pixel_array,  bytes_per_pix=2, is_signed=False, is_float=False):
    """
    Function to create completely new DICOM file.
    :param filename: Name of the file to be written.
    :param pixel_array: 2D or 3D numpy array containing pixel values.
    :param bytes_per_pix: How many bytes are used to encode one pixel.
    :param is_signed: Are signed or unsigned types used to encode image.
    :param is_float: currently not used
    :return: 
    """
    file_meta = Dataset()
    # The Secondary Capture (SC) Image Information Object Definition (IOD) specifies images that are converted from
    # a non-DICOM format to a modality independent DICOM format.
    file_meta.MediaStorageSOPClassUID = 'Secondary Capture Image Storage'
    file_meta.MediaStorageSOPInstanceUID = '1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780'
    file_meta.ImplementationClassUID = '1.3.6.1.4.1.9590.100.1.0.100.4.0'
    # Since we don't want to store any additional info in the header, we set it to x00
    ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b'0' * 128)

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
    # How many bits are allocated to store pixel info
    ds.BitsAllocated = bytes_per_pix * 8
    # How many bits are used to store pixel info
    ds.BitsStored = bytes_per_pix*8
    # Whether signed or unsigned numbers are used
    if is_signed:
        ds.PixelRepresentation = 1
    else:
        ds.PixelRepresentation = 0
    # ds.SmallestImagePixelValue = '\\x00\\x00'
    # ds.LargestImagePixelValue = '\\xff\\xff'

    # Read from data the dimensions.
    if len(pixel_array.shape) == 3:
        ds.NumberOfFrames = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]
        ds.Rows = pixel_array.shape[2]
    else:
        ds.Columns = pixel_array.shape[0]
        ds.Rows = pixel_array.shape[1]

    try:
        err_str = 'The file could not be created because of: '

        data_type = recognize_type(bytes_per_pix, is_signed, is_float)
        if pixel_array.dtype != data_type:
            pixel_array = pixel_array.astype(data_type)
        ds.PixelData = pixel_array.tostring()

        ds.save_as(filename)
        print('Writing complete!')
        return True
    except ValueError as ve:
        print(err_str+str(ve))
        return False
    except Exception as e:
        print(err_str+str(e))


def get_help():
    print('#'*50)
    print('This is a binary -> DICOM converter created by Rafal Maselek.')
    print('Usage:')
    print("python binary2DICOM.py <arguments>")
    print("Required arguments:")
    print("\t<input file name (str)>\n\t<output file name (str)>\n\t<image width (int)>\n\t<image height(int)>\n\t<no. of frames (int)>")
    print("Optional arguments:")
    print("\t<bytes per pixel(int)>\n\t<is it signed int (1/0)>\n\t<is it float (1/0)>\n\t<endian type> (big/little)")
    print('In order to create dummy files (2D or 3D gradient images) type: \npython3 binary2DICOM --test2d OR python3 binary2DICOM --test3d')
    print('#'*50)


def test2d():
    """
    Function creates a dummy file with a 2D gradient.
    :return: True
    """
    x = np.arange(16).reshape(16,1) # tworzymy gradient 1D
    pixel_array = (x + x.T) * 16 # z tablicy robimy gradient 2D i wygladzamy
    pixel_array = np.tile(pixel_array,(4,4)) # powielamy 4 razy wzdluz X i Y
    write_dicom('pretty2d.dcm', pixel_array)
    return True


def test3d():
    """
    Function creates a dummy file with a 2D gradient, repeated on 4 slices.
    :return: 
    """
    x = np.arange(16).reshape(16, 1)  # tworzymy gradient 1D
    pixel_array = (x + x.T) * 16  # z tablicy robimy gradient 2D i wygladzamy
    pixel_array = np.tile(pixel_array, (4, 4, 4))
    write_dicom('pretty3d.dcm', pixel_array)
    return True


def convert(in_file, out_file, width, height, frames, bytes_per_pix=2, is_signed=False, is_float=False, byte_order=''):
    image_arr = read_binary(in_file, width, height, frames, bytes_per_pix, is_signed, is_float, byte_order)
    return write_dicom(out_file, image_arr, bytes_per_pix, is_signed, is_float)


if __name__ == "__main__":
    bytes_per_pix = 2
    is_signed = False
    is_float = False
    byte_order = ''
    result = True
    # Checking user's input
    if(sys.argv[1][:2] == '--'):
        # print(sys.argv[1])
        if sys.argv[1][2:] == 'test2d':
            result = test2d()
        elif sys.argv[1][2:] == 'test3d':
            result = test3d()
        elif sys.argv == 'help':
            get_help()
        else:
            print("Unrecognized first argument!")
    else:
        sys_len = len(sys.argv)
        if sys_len < 6:
            get_help()
        if sys_len >= 7:
            bytes_per_pix = int(sys.argv[6])
        if sys_len >= 8:
            is_signed = bool(sys.argv[7])
        if sys_len >= 9:
            is_float = bool(sys.argv[8])
        if sys_len == 10:
            byte_order = sys.argv[9]
        if sys_len > 10:
            print("WARNING: Too many arguments passed. Additional arguments will be omitted.")

        # Performing conversion
        result = convert(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]),\
                         bytes_per_pix, is_signed, is_float, '')

    if result:
        print('Action complete!')
    else:
        print('Action could not be done!')





