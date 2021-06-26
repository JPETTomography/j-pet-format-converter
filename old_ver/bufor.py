"""
Writes DICOM tags into the N x 4 array

:param args: interfile header file dictionary
:returns: N x 4 array with written DICOM tags
"""
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

	def convert():
		'''# Create some temporary filenames
	suffix = '.dcm'
	filename_little_endian = tempfile.NamedTemporaryFile(suffix=suffix).name
	filename_big_endian = tempfile.NamedTemporaryFile(suffix=suffix).name'''

	print("Setting file meta information...")
	# Populate required values for file meta information
	file_meta = Dataset()
	file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
	file_meta.MediaStorageSOPInstanceUID = "1.2.3"
	file_meta.ImplementationClassUID = "1.2.3.4"


	'''# Generate from template
	CTDatasetFactory().PatientName = 'van Haarlem^Anouk'  #  generated random name
	CTDatasetFactory().PatientName = 'Loreal^Casper'      #  generated random name

	# Overwrite arbitrary DICOM elements
	file_meta.CTDatasetFactory(PatientSex='M', PatientName='Smith^Harry')
	file_meta.PatientName = 'Smith^Harry'
	file_meta.PatientSex  = 'M'

	# generated UIDs and dates are valid DICOM
	CTDatasetFactory().StudyTime        = '130624.929'
	CTDatasetFactory().StudyDate        = '20110508'
	CTDatasetFactory().StudyInstanceUID = '1.2.826.0.1.3680'''

	print("Setting dataset values...")
	# Create the FileDataset instance (initially no data elements, but file_meta
	# supplied)
	ds = FileDataset(args['out_file'], {},
                 file_meta=file_meta, preamble=b"\0" * 128)

	# Add the data elements -- not trying to set all required here. Check DICOM
	# standard
	ds.PatientName = "Test^Firstname"
	ds.PatientID = "123456"

	# Set the transfer syntax
	if args['byte_order'] == 'little':
		ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
		ds.is_little_endian = True
		ds.is_implicit_VR = True
	elif args['byte_order'] == 'big':
		ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRBigEndian
		ds.is_little_endian = False
		ds.is_implicit_VR = False
	else:
		print("ERROR! BYTEORDER IS NOT SET")

	# Set creation date/time
	dt = datetime.datetime.now()
	ds.ContentDate = dt.strftime('%Y%m%d')
	timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
	ds.ContentTime = timeStr

	if args['is_signed']:
		ds.PixelRepresentation = 1
	else:
		ds.PixelRepresentation = 0

	ds = b2d.write_meta(meta_arr,ds)

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

		data_type = b2d.recognize_type(args['bytes_per_pix'], args['is_signed'], args['is_float'])
		if pixel_array.dtype != data_type:
			pixel_array = pixel_array.astype(data_type)
			ds.PixelData = pixel_array.tobytes()
	except ValueError as ve:
		print(err_str+'ValueError '+str(ve))
		return -1
	except FileExistsError as fe:
		print(err_str+'FileExistsError '+str(fe))
		return -1
	except Exception as e:
		print(err_str+str(e))
		return -1

	ds.save_as(args['out_file'].replace('.dcm', '') + '.dcm')