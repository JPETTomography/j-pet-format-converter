#Interfile to DICOM converter
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl
#
#This script converts given file in interfile data format to DICOM

import sys
import binary2DICOM as b2d

"""
Reads Interfile header file.

:param filename: name of the header file
:returns: dictionary containing header data 

"""
def readHeader(filename):

	meta_dict = {}

	with open(filename,"r") as f:

		start_line = f.readline()

		if start_line == "!INTERFILE := \n":

			bufor = f.readlines()

			for line in bufor:
				line = line.strip('!\n')
				line = line.split(' := ')
				if line[0] != '':
					if "end" in line[0].lower():
						return meta_dict
					elif "general" not in line[0].lower() :
						meta_dict[line[0]] = line[1]


			print("ERROR! COULDN'T FIND END OF INTERFILE HEADER KEY!")
			sys.exit(1)

		else:
			print("ERROR! COULDN'T FIND START OF INTERFILE HEADER KEY!")
			sys.exit(1)

	print("ERROR! INVALID FILE!")
	sys.exit(1)

"""
Recognizes data type taken from a header file

:param bytes_per_pix: value from 'number of bytes per pixel' key
:type: value from  'number format' key
:returns: Numpy type
"""
def recognizeTypeInterfile(bytes_per_pix,type):
	isSigned = lambda var_type: "unsigned" not in var_type
	isFloat = lambda var_type: "float" in var_type

	try:
		bytes_per_pix = int(bytes_per_pix)
	except ValueError:
		print("ERROR! GOT",type(bytes_per_pix),"INSTEAD OF INT!")
		sys.exit(1)

	return b2d.recognize_type(bytes_per_pix,isSigned(type),isFloat(type))



def main():
	d = readHeader('recon_3_1_it3.hdr')


if __name__ == '__main__':
	main()