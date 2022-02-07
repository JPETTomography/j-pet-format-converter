# j-pet-format-converter
## version 2.0.2
### Author: Rafał Masełek, Mateusz Kruk
### Email: rafal.maselek@ncbj.gov.pl, mateusz64.kruk@student.uj.edu.pl
### Modifications: Wojciech Krzemien 

This script enables converting Interfile files to DICOM file format and importing meta-data from external file.

### Installation:
**Prerequisites:**
+ Python (vers. 3.X.X recommended)
+ Numpy  (python library)
+ pyDicom (python library)
+ setuptools >= 42
+ wheel (python library)

If you use Debian/Ubuntu/Linux Mint you can install python3 using 'apt-get install' command:
```bash
sudo apt-get install python3 
```

If you use Mac OS X and have Homebrew installed, you can type:
```bash
sudo brew install python3
```

If you don't have Homebrew, then get it using the following command:

sudo /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

This will require providing root's (system administrator's) password. Python3 can be safely installed alongside python2, which is still (unfortunately) the default
python distribution on many Linux systems.

Additional python libraries can be installed using 'pip3' application, which should be installed with python3 from version 3.4.
If you do not have it, you can install it by running:
>sudo apt-get install python3-pip 

To get the necessary libraries, simply run the following commands in the terminal:
>sudo pip3 install numpy

>sudo pip3 install pydicom

If you have any of the requirements already installed, you will receive a message informing you about it. You can then proceed to the next step.

### Usage:
To learn how to use script simply download the repository and run in terminal:
>python3 binary2DICOM.py --help

**Usage example:**
This is an example command used to convert Gate output to DICOM format.
File with simulated data is called in this example **collimator_20**.
>python3 binary2DICOM.py --meta meta.txt collimator_20 collimator_20-conv.dcm 256 256 256 -bpp 4 -int -bo little
+ **python3 binary2DICOM.py** uses python3 to run the script
+ **--meta meta.txt** specifies that external file with meta data is used; it is called 'meta.txt' and is located in the same directory as the binary2DICOM.py script
+ **collimator_20** name of the binary image file (input file for script)
+ **collimator_20-conv.dcm** name of the output file, note the '.dcm' extension
+ **256 256 256** X, Y and Z(no of frames) dimensions of encoded images (size in pixels)
+ **-bpp 4** defines that 4 bytes were used to encode every pixel of input data (if you don't know encoding type, then ask the maker of the input file)
+ **-int** specifies that signed integers were used to encode input image (use '-uint' for unsigned integers)
+ **-bo little** specifies the byte order used to encode binary image; supported are **little/big**

Not all parameters are necessary, optional ones have default values. You can get more information by using **--help** flag.

### Supported encodings:
The script is capable of reading binary images encoded using signed or unsigned integers, 1/2/4/8 bytes per pixel.
In the future it might be developed to manage file encoded using floating point numbers.

### External meta data file:
External file with metadata must have apropriate format (see meta.txt):
You have to specify: **group tag**, **element tag**, **VR** and **value**.
All these elements have to be separated using comma.
String values need to be inside **'** characters.
Dot is used as a decimal delimiter.
You can write comments using hash symbol (#) -- following characters are ignored.

### Using binary2DICOM as module:
The script can be used as a python module in external program. To use it you have to import binary2DICOM to your script:
>from binary2DICOM import convert

Then you have to call convert() method, providing special dictionary as an argument.
The dictionary must have the following structure:


{'meta': (meta_data_file_path, STRING),\
'in_file': (input_data_file_path, STRING),\
'out_file': (output_data_file_path, STRING),\
'width': (INT),\
'height': (INT),\
'frames': (INT),\
'is_signed': (BOOL),\
'byte_order': ('little' OR 'big'),\
'bytes_per_pix': (INT),\
'is_float': (BOOL)}
    
Key-value pairs in the dictionary correspond to input parameters.
You code should look like this:

```convert({'meta': 'meta.txt', 'width': 256, 'is_signed': True, 'in_file': 'collimator_20', 'byte_order': 'little', 'height': 256, 'frames': 256, 'bytes_per_pix': 4, 'out_file': 'collimator_20-conv.dcm', 'is_float': False})```

Of course you can store dictionary in a variable and pass this variable to the *convert()* function.
### Viewing the results:
There are many applications to visualize images in DICOM files. Personally, I recommend using Amide:

http://amide.sourceforge.net/

To open a .dcm file use the FILE menu:\
File > Import File(specify) > DICOM 3.0 via (X)MedCon.

Amide uses a very useful tool called [(X)MedCon](http://xmedcon.sourceforge.net/),
which can be downloaded from project's website or system's repositories, and it can be used alone to open DICOM files
(but Amide provides better visualization).

To install (X)MedCon on Debian/Ubuntu/Linux Mint from repositories:
>sudo apt-get install xmedcon

In order to open DICOM file from Terminal, use command:
>xmedcon -f name_of_file.dcm

(X)MedCon has many other options and supported formats, see project's documentation for 
details.
