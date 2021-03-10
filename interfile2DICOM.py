#Interfile to DICOM converter
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl
#
#This script converts given file in interfile data format to DICOM

import sys
import argparse
import binary2DICOM as b2d
from . import Interfile
import datetime
import time

"""
Reads Interfile header file.

:param filename: name of the header file
:returns: dictionary containing header data or ValueError in case of incorrect argument

"""
def readHeader(filename):

	meta_dict = {}

	try:
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
							try:
								meta_dict[line[0]] = int(line[1])
							except ValueError:
								meta_dict[line[0]] = line[1]


				print("ERROR! COULDN'T FIND END OF INTERFILE HEADER KEY!")
				raise ValueError

			else:
				print("ERROR! COULDN'T FIND START OF INTERFILE HEADER KEY!")
				raise ValueError

	except FileNotFoundError:
		print("ERROR! INVALID FILENAME!")
		raise ValueError

"""
Recognizes data type taken from a header file

:param bytes_per_pix: value from 'number of bytes per pixel' key
:type: value from  'number format' key
:returns: Numpy type
"""
def recognizeTypeInterfile(bytes_per_pix,type):
	isSigned = lambda var_type: "unsigned" not in var_type
	isFloat = lambda var_type: "float" in var_type

	if type not in ["int","unsigned int", "float", "unsigned float"]:
		print("ERROR! WRONG TYPE INPUT!")
		raise ValueError

	try:
		bytes_per_pix = int(bytes_per_pix)
	except ValueError:
		print("ERROR! GOT INCORRECT BYTES PER PIX INPUT!")
		raise ValueError

	return b2d.recognize_type(bytes_per_pix,isSigned(type),isFloat(type))

"""
Parses header file values into the dictionary supported in binary2DICOM

:param head: Dictionary generated from .hdr file
:returns: Dictionary with keys matching those in binary2DICOM
"""
def parseHead(head):

	if head:

		args_keys = ["in_file","out_file","width","height","frames","bytes_per_pix","is_signed","byte_order"]
		head_keys = ["name of data file","patient name","matrix size [1]","matrix size [2]","matrix size [3]","number of bytes per pixel","number format","imagedata byte order"]

		if len(args_keys) == len(head_keys):

			args = {}
			order = lambda order_type: "little" if "little" in order_type.lower() else "big" if "big" in order_type.lower() else "system" if "system" in order_type.lower() else " "
			connect = lambda x,y: [x,y]
			keys = map(connect,args_keys,head_keys)

			for key_pair in keys:
				try:
					if "matrix" in key_pair[1]:
						args[key_pair[0]] = head[key_pair[1]] if (head["number of dimensions"] >= int(key_pair[1][-2])) else 0

					elif "order" in key_pair[1]:
						args[key_pair[0]] = order(head[key_pair[1]])

					elif "format" in key_pair[1]:
						args[key_pair[0]] = "unsigned" not in head[key_pair[1]]

					else:
						args[key_pair[0]] = head[key_pair[1]]

				except KeyError as e:
					print("ERROR! WRONG HEADER KEY: "+e.args[0])
					args[key_pair[0]] = ""

				except ValueError:
					print("ERROR! INCORRECT HEADER KEY (penultimate character is not a number): "+key_pair[1])
					args[key_pair[0]] = 0


			args["is_float"] = False

			return args

		else:
			print("ERROR! NUMBER OF ARGS AND HEADER KEYS DOES NOT MATCH: "+ len(args_keys) +" "+ len(head_keys))
			raise ValueError

	else:
		print("ERROR! DICTIONARY IS EMPTY!")
		raise ValueError


#TODO: do write meta file from interfile header
def writeMeta(args):

	meta_arr = []
	
	#redundant
	#date = str(datetime.date.today()).replace('-', '')
	#now = str(time.time())

	#Patient [C.7.1.1]
	meta_arr.append([0x0010,0x0010,'PN',args['patient name']]) #Patient's name
	meta_arr.append([0x0010,0x0020,'LO','']) #Patient's ID
	meta_arr.append([0x0010,0x0022,'CS','']) #Type of Patient's ID
	meta_arr.append([0x0010,0x0030,'DA','']) #Patient's Birth Date
	meta_arr.append([0x0010,0x0040,'CS','']) #Patient's Sex
	meta_arr.append([0x0040,0xE020,'CS','DICOM']) #Type of Instances
	meta_arr.append([0x0008,0x1150,'UI','']) #Referenced SOP Class UID
	meta_arr.append([0x0008,0x1155,'UI','']) #Referenced SOP Instance UID


	#Study [C.7.2.1]
	meta_arr.append([0x0020,0x000D,'UI','']) #Study Instance UID
	meta_arr.append([0x0008,0x0018,'UI','']) #SOP Instance UID
	meta_arr.append([0x0008,0x0020,'DA','']) #Study date
	meta_arr.append([0x0008,0x0030,'TM','']) #Study time
	meta_arr.append([0x0008,0x0090,'PN','']) #Referring Physician's Name

	#Series [C.7.3.1]
	meta_arr.append([0x0020,0x000E,'UI','']) #Series Instance UID
	meta_arr.append([0x0008,0x0060,'CS','']) #Modality
	meta_arr.append([0x0020,0x0011,'IS','']) #Series Number


	#Equipement [C.8.6.1]
	meta_arr.append([0x0008,0x0064,'CS','']) #Conversion type

	#General Image [C.7.6.1]
	meta_arr.append([0x0020,0x0013,'IS','']) #Instance Number

	#Image Pixel [C.7.6.3]
	meta_arr.append([0x7FE0,0x0010,'OB','']) #Pixel Data
	meta_arr.append([0x0028,0x0002,'US','']) #Samples per pixel
	meta_arr.append([0x0028,0x0004,'CS','']) #Photometric interpolation
	meta_arr.append([0x0028,0x0010,'US','']) #Rows
	meta_arr.append([0x0028,0x0011,'US','']) #Columns
	meta_arr.append([0x0028,0x0100,'US','']) #Bits Allocated
	meta_arr.append([0x0028,0x0101,'US','']) #Bits stored
	meta_arr.append([0x0028,0x0102,'US','']) #High bit
	meta_arr.append([0x0028,0x0103,'US','']) #Bit representation

	#SC Image [C.8.6.2]
	meta_arr.append([0x0008,0x0104,'LO','']) #Code Meaning


	#SOP Common [C.12.1]
	meta_arr.append([0x0008,0x0016,'UI','']) #SOP Class UID
	meta_arr.append([0x0008,0x0018,'UI','']) #SOP Instance UID
	meta_arr.append([0x0008,0x0070,'LO','']) #Manufacturer

	'''
	Old version of tags, kept just in case, if the set above is not enough

	#Type 1 tags
	meta_arr.append([0x0010,0x0022,'CS','']) #Type of Patient ID
	meta_arr.append([0x0010,0x0214,'LO','']) #Strain Stock Number
	meta_arr.append([0x0010,0x0217,'LO','']) #Strain Source
	meta_arr.append([0x0010,0x0222,'UC','']) #Genetic Modifications Description
	meta_arr.append([0x0010,0x0217,'LO','']) #Genetic Modifications Nomenclature
	meta_arr.append([0x0008,0x0054,'AE','']) #Retrieve AE Title
	meta_arr.append([0x0088,0x0140,'UI','']) #Storage Media File-set UID
	meta_arr.append([0x0008,0x0102,'SH','']) #Coding Scheme Designator
	meta_arr.append([0x0008,0x010A,'CS','']) #Coding Scheme URL Type
	meta_arr.append([0x0008,0x010E,'UR','']) #Coding Scheme URL
	meta_arr.append([0x0008,0x0105,'CS','']) #Mapping Resource
	meta_arr.append([0x0008,0x0106,'DT','']) #Context Group Version
	meta_arr.append([0x0008,0x010F,'CS','']) #Context Identifier


	#Type 2 tags - can be empty if unkown
	meta_arr.append([0x0020,0x0010,'SH','']) #Study ID
	meta_arr.append([0x0020,0x0020,'CS','']) #Patient Orientation'''

	return meta_arr

def main():
	dictionary = Interfile.load("recon_3_1_it3.hdr")
	print("IT JUST WORKS")
	#[TODO] management of any interfile file


if __name__ == '__main__':
	main()