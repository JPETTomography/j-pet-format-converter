# j-pet-format-converter
##version 1.1
### Author: Rafal Maselek
### Email: rafal.maselek@ncbj.gov.pl

This script enables converting raw 3D binary images to DICOM file format and importing meta-data from external file.

Prerequisites:
Python 3, Numpy, pyDicom

To learn how to use script simply download it and run in terminal:
> python3 binary2DICOM --help

The script is capable of reading binary images encoded using signed or unsigned integers, 1/2/4/8 bytes per pixel.

External file with metadata must have apropriate format (see meta.txt):
You have to specify: group tag, element tag, VR and value.
All these elements have to be separated using comma.
String values need to be inside '' characters.
Dot is used as a decimal delimiter.
You can write comments using hash symbol -- everything after it is ignored.


