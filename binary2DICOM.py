# binary2DICOM converter
# Author: Rafal Maselek
# Email: rafal.maselek@ncbj.gov.pl
#
# This script enables converting raw 3D binary images to DICOM file format and importing meta-data from external file.

import sys
from dicom.dataset import Dataset, FileDataset
import numpy as np
import datetime, time

version = "version 1.0 features included:\n\tReading raw binary file with image\n\tReading file with meta-data\n\tCreating\
 a new DICOM file\n\tReading image parameters from meta-data"


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
            raise ValueError('ERROR: Invalid type declared!')
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
            raise ValueError('ERROR: Invalid type declared!')


def read_meta(filename):
    """
    A naive parser for DICOM meta-data.
    :param filename: Contains meta-data in a format: <group tag> , <element tag> , <VR>, <value> Commas are delimiters.
    :return: An array N x 3, where N is the number of correctly parsed lines.
    """
    meta_arr = []
    line_no = 0
    lines_with_data = 0
    with open(filename) as f:
        for line in f:
            line_no += 1
            line = line.partition('#')[0]
            line = line.strip()
            line = line.split(',')
            err_str = ' could not be parsed correctly!'
            if len(line[0]) > 0:
                lines_with_data +=1
                if len(line) > 4:
                    print("WARNING: Line "+str(line_no)+" contains more values than required. Please, check it.")
                try:
                    if len(str(line[2]).strip()) != 2:
                        raise ValueError('VR should consist of exactly 2 characters! VR parsed:'+str(line[2]).strip())
                    line_data = [int(line[0], 16), int(line[1], 16), str(line[2]).strip()]
                    # parsing the value
                    if line[3][0] == '\'' or line[3][-1] == '\'':
                        # parse as string
                        line_data.append(line[3].replace('\'', '').strip())
                    elif line[3].find('.') != -1:
                        # parse as float
                        line_data.append(float(line[3]))
                    else:
                        # parse as int
                        line_data.append(int(line[3]))
                    # print(line_data)
                    meta_arr.append(line_data)

                except ValueError as e:
                    print('WARNING: Line '+str(line_no)+err_str + " Wrong value!" + "ERR MSG: "+str(e))
                except IndexError as e:
                    print('WARNING: Line '+str(line_no)+err_str + " Tags or/and value are missing!" + "ERR MSG: "+str(e))
    print("Reading meta-data is complete! " + str(len(meta_arr))+'/'+str(lines_with_data)+' were parsed correctly.')
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
    print('Reading image data is complete!')
    return resh_arr


def write_dicom(filename, pixel_array,  bytes_per_pix=2, is_signed=False, is_float=False, meta_arr = []):
    """
    Function to create completely new DICOM file.
    :param filename: Name of the file to be written.
    :param pixel_array: 2D or 3D numpy array containing pixel values.
    :param bytes_per_pix: How many bytes are used to encode one pixel.
    :param is_signed: Are signed or unsigned types used to encode image.
    :param is_float: currently not used
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

    # Here meta-data is put into the Data Set. It can override hardcoded values, but parameters providided as program
    # arguments will be inserted no matter what is in the meta-data file.
    ds = write_meta(meta_arr, ds)

    # How many bits are allocated to store pixel info
    ds.BitsAllocated = bytes_per_pix * 8
    # How many bits are used to store pixel info
    ds.BitsStored = bytes_per_pix*8
    # Whether signed or unsigned numbers are used
    if is_signed:
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
        err_str = 'The file could not be created because of: '

        data_type = recognize_type(bytes_per_pix, is_signed, is_float)
        if pixel_array.dtype != data_type:
            pixel_array = pixel_array.astype(data_type)
        ds.PixelData = pixel_array.tostring()

        ds.save_as(filename.replace('.dcm', '') + '.dcm')
        print('Writing to DICOM file is complete!')
        return True
    except ValueError as ve:
        print(err_str+'ValueError '+str(ve))
        return False
    except FileExistsError as fe:
        print(err_str+'FileExistsError '+str(fe))
    except Exception as e:
        print(err_str+str(e))
        return False
    return True


def get_help():
    print('#'*50)
    print('This is a binary -> DICOM converter created by Rafal Maselek.')
    print('Type python3 binary2DICOM --version to get version info.')
    print('Usage:')
    print("python binary2DICOM.py <arguments>")
    print("Required arguments when no header is used:")
    print("\t<input file name (str)>\n\t<output file name (str)>\n\t<image width (int)>\n\t<image height(int)>\n\t<no. of frames (int)>")
    print("Optional arguments:")
    print("\t<bytes per pixel(int)>\n\t<is it signed int (1/0)>\n\t<is it float (1/0)>\n\t<endian type> (big/little)")
    print('In order to create dummy files (2D or 3D gradient images) type: \npython3 binary2DICOM --test2d OR python3 binary2DICOM --test3d')
    print('Type to use meta-data file:')
    print('python3 binary2DICOM --meta <file with meta> <other arguments>')
    # print('When using a meta-file you have to provide only the name of meta- in- out- files. Parameters can be be set in the meta file.')
    print('#'*50)


def test2d():
    """
    Function creates a dummy file with a 2D gradient.
    :return: True
    """
    print('Making 2d image filled with gradient squares.')
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
    print('Making 3d image filled with gradient squares.')
    x = np.arange(16).reshape(16, 1)  # tworzymy gradient 1D
    pixel_array = (x + x.T) * 16  # z tablicy robimy gradient 2D i wygladzamy
    pixel_array = np.tile(pixel_array, (4, 4, 4))
    write_dicom('pretty3d.dcm', pixel_array)
    return True


def convert(in_file, out_file, width, height, frames, bytes_per_pix=2, is_signed=False, is_float=False, byte_order='', meta_file=''):
    meta_arr = []
    try:
        if meta_file != '':
            meta_arr = read_meta(meta_file)
    except FileNotFoundError as fnfe:
        print("WARNING: Meta-data was not loaded, because the file was not found: "+str(fnfe))
        print("I will now proceed to reading an image data.")
    image_arr = read_binary(in_file, width, height, frames, bytes_per_pix, is_signed, is_float, byte_order)
    if_success = write_dicom(out_file, image_arr, bytes_per_pix, is_signed, is_float, meta_arr)
    return if_success

if __name__ == "__main__":
    in_file = ''
    out_file = ''
    meta_file = ''
    width = 0
    height = 0
    frames = 0
    bytes_per_pix = 2
    is_signed = False
    is_float = False
    byte_order = ''
    result = True
    add_arg = 0
    conv = True
    # Checking user's input
    sys_len = len(sys.argv)
    if sys_len > 1:
        if sys.argv[1][:2] == '--':
            # print(sys.argv[1])
            if sys.argv[1][2:] == 'test2d':
                result = test2d()
                conv = False
            elif sys.argv[1][2:] == 'test3d':
                result = test3d()
                conv = False
            elif sys.argv[1][2:] == 'help':
                get_help()
                conv = False
            elif sys.argv[1][2:] == 'version':
                print(version)
            elif sys.argv[1][2:] == 'meta':
                print('I will try to read meta-data from external file.')
                meta_file = sys.argv[2]
                add_arg = 2
            else:
                print("WARNING: Unrecognized first argument! I will ignore it and perform conversion.")
                add_arg = 1

        if conv:
            if sys_len < 6+add_arg:
                print('ERROR: Not enough arguments were provided. GET:'+str(sys_len-1)+" NEEDED:"+str(5+add_arg))
                print('Type \'python3 binary2DICOM --help\' for instructions')
                result = False
            else:
                in_file = sys.argv[1+add_arg]
                out_file = sys.argv[2+add_arg]
                width = int(sys.argv[3+add_arg])
                height = int(sys.argv[4+add_arg])
                frames = int(sys.argv[5+add_arg])

                if sys_len >= 7+add_arg:
                    bytes_per_pix = int(sys.argv[6+add_arg])
                if sys_len >= 8+add_arg:
                    is_signed = bool(sys.argv[7+add_arg])
                if sys_len >= 9+add_arg:
                    is_float = bool(sys.argv[8+add_arg])
                if sys_len == 10+add_arg:
                    byte_order = sys.argv[9+add_arg]
                if sys_len > 10+add_arg:
                    print("WARNING: Too many arguments passed. Additional arguments will be omitted.")

                # Performing conversion
                result = convert(in_file, out_file, width, height, frames, bytes_per_pix, is_signed, is_float, '', meta_file)
    if result:
        print('Work is complete!')
    else:
        print('Work could not be done!')





