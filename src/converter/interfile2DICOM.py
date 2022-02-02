#Interfile to DICOM converter
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl
#
#This script converts given file in interfile data format to DICOM

import os
import tempfile

import pydicom
from pydicom.dataset import Dataset, FileDataset

import sys
import argparse
#import binary2DICOM as b2d
import json
import datetime
import time

# Dicom generator for testing purposes
# [!]
from dicomgenerator.exporter import export
from dicomgenerator.factory import CTDatasetFactory

#this module somehow doesn't work
#import interfile

supported_versions = ["3.1"]

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


				print("ERROR! Couldn't find end of interfile header key!")
				raise ValueError

			else:
				print("ERROR! Couldn't find start of interfile header key!")
				raise ValueError

	except FileNotFoundError:
		print("ERROR! Invalid filename!")
		raise ValueError

"""
Reads JSON file.

:param filename: name of the JSON file
:returns: dictionary containing header data or ValueError in case of incorrect argument

"""
def readJSON(filename):

	#[TODO] add more JSON arguments to be accepted
	json_args = []

	with open(filename,"r") as f:
		json_args = json.load(f)

	try:
		return readHeader(json_args["filename"])
	except KeyError:
		print("ERROR! Incorrect JSON file!")
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
		print("ERROR! Wrong type input!")
		raise ValueError

	try:
		bytes_per_pix = int(bytes_per_pix)
	except ValueError:
		print("ERROR! Got incorrect bytes per pixel input!")
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
					print("ERROR! Wrong header key: "+e.args[0])
					args[key_pair[0]] = ""

				except ValueError:
					print("ERROR! Incorrect character key (penultimate character is not a number): "+key_pair[1])
					args[key_pair[0]] = 0


			args["is_float"] = False

			return args

		else:
			print("ERROR! Number of args and header keys does not match: "+ len(args_keys) +" "+ len(head_keys))
			raise ValueError

	else:
		print("ERROR! Dictionary is empty!")
		raise ValueError


#write_meta pushed to bufor.py

def writeMeta(args):

	meta_arr = []
	
	#redundant
	#date = str(datetime.date.today()).replace('-', '')
	#now = str(time.time())

	#Patient [C.7.1.1]
	meta_arr.append([0x0010,0x0010,'PN',args['patient name']]) #Patient's name [2]
	meta_arr.append([0x0010,0x0020,'LO','']) #Patient's ID [2]
	meta_arr.append([0x0010,0x0030,'DA','']) #Patient's Birth Date [2]
	meta_arr.append([0x0010,0x0040,'CS','']) #Patient's Sex [2]
	meta_arr.append([0x0040,0xE020,'CS','DICOM']) #Type of Instances [1]
	meta_arr.append([0x0008,0x1150,'UI','Secondary Capture Image Storage']) #Referenced SOP Class UID [1]
	meta_arr.append([0x0008,0x1155,'UI','1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780']) #Referenced SOP Instance UID [1]


	#Study [C.7.2.1]
	meta_arr.append([0x0020,0x000D,'UI','1.3.6.1.4.1.9590.100.1.1.124313977412360175234271287472804872093']) #Study Instance UID [1]
	meta_arr.append([0x0008,0x0020,'DA','']) #Study date [2]
	meta_arr.append([0x0008,0x0030,'TM','']) #Study time [2]
	meta_arr.append([0x0008,0x0090,'PN','']) #Referring Physician's Name [2]

	#Series [C.7.3.1]
	meta_arr.append([0x0020,0x000E,'UI','1.3.6.1.4.1.9590.100.1.1.369231118011061003403421859172643143649']) #Series Instance UID [1]
	meta_arr.append([0x0008,0x0060,'CS','PT']) #Modality [1]
	meta_arr.append([0x0020,0x0011,'IS','']) #Series Number [2]


	#Equipement [C.8.6.1]
	meta_arr.append([0x0008,0x0064,'CS','WSD']) #Conversion type [1] ?

	#General Image [C.7.6.1]
	meta_arr.append([0x0020,0x0013,'IS','']) #Instance Number [2]

	#Image Pixel [C.7.6.3]

	meta_arr.append([0x0028,0x0002,'US',1]) #Samples per pixel [1]
	meta_arr.append([0x0028,0x0004,'CS','MONOCHROME2']) #Photometric interpolation [1]
	meta_arr.append([0x0028,0x0100,'US',8 * args['number of bytes per pixel']]) #Bits Allocated [1]
	meta_arr.append([0x0028,0x0101,'US',8 * args['number of bytes per pixel']]) #Bits stored [1]
	meta_arr.append([0x0028,0x0102,'US',15]) #High bit [1]
	meta_arr.append([0x0028,0x0103,'US',1]) #Bit representation [1]

	#SC Image [C.8.6.2]
	meta_arr.append([0x0008,0x0104,'LO','test']) #Code Meaning [1]


	#SOP Common [C.12.1]
	meta_arr.append([0x0008,0x0016,'UI','Secondary Capture Image Storage']) #SOP Class UID [1]
	meta_arr.append([0x0008,0x0018,'UI','1.3.6.1.4.1.9590.100.1.1.111165684411017669021768385720736873780']) #SOP Instance UID [1]
	meta_arr.append([0x0008,0x0070,'LO','NCBJ']) #Manufacturer


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

def convert(args,pixel_array,meta_arr = []):
	export(dataset=CTDatasetFactory(), path="/tmp/dummy_dicom/dicom.dcm")


def main():

	#checking if the filename is in the arguments list
	#[TODO] multiple DICOM converions
	if len(sys.argv) != 2:
		print("ERROR! Got {} arguments instead of 2!".format(len(sys.argv)))
		sys.exit(1)

	else:

		dictionary = []

		#checking if the file is a JSON or a Interfile header file
		if (sys.argv[1][-4:] == ".hdr"):
			dictionary = readHeader(sys.argv[1])
		elif (sys.argv[1][-5:] == ".json"):
			print("WARNING! This version of Interfile to DICOM does not use any other JSON values than 'filename' value!")
			dictionary = readJSON(sys.argv[1])

		#CASToR keys version check
		if dictionary["CASToR version"] not in supported_versions:
			#[TODO] LOAD KEY TEMPLATE FROM A FILE, DEPENDING ON THE CASToR VERSION
			print("ERROR! Your CASToR version ({}) is not currently supported!".format(dictionary["CASToR version"]))
		
		#main conversion
		else:
			#convert("test")
			arguments = parseHead(dictionary)
			array = b2d.read_binary(arguments)
			meta_arr = writeMeta(dictionary)
			convert(arguments,array,{})

		#[TODO] solve warnings in write DICOM

if __name__ == '__main__':
	main()