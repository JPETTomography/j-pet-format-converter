#Interfile to DICOM converter
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl
#
#This script converts given file in interfile data format to DICOM

import sys
import argparse
import binary2DICOM as b2d

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
#def writeMeta(args):
	#yes

def main():
	head_dict = readHeader('recon_3_1_it3.hdr')
	args_dict = parseHead(head_dict)

	arr = b2d.read_binary(args_dict)

	print(arr)

	#b2d.write_dicom(args_dict,arr) writing an invalid file [TODO] FIX IT


if __name__ == '__main__':
	main()