import interfile2DICOM as i2d
import os
import unittest
import numpy as np

class HeaderTest(unittest.TestCase):

	def test_readHeader(self):

		print("\n")

		correct_start = "!INTERFILE := \n"
		correct_key = "!test_key := test_value\n"
		correct_end = "!END OF INTERFILE := "

		with open("test.hdr","w") as f:
			f.write(correct_start)
			f.write(correct_key)
			f.write(correct_end)

		try:
			d = i2d.readHeader("test.hdr")
		except ValueError:
			self.fail("ERROR! readHeader() THREW ValueError WITH CORRECT DATA")
		
		self.assertEqual(d["test_key"],"test_value","ERROR! WRONG VALUE BINDED TO KEY IN readHeader()")

		with open("test1.hdr","w") as f:
				f.write(correct_key)

		with open("test2.hdr","w") as f:
				f.write(correct_start)

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT FILENAME:")
			d = i2d.readHeader("t")

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT INTERFILE START:")
			d = i2d.readHeader("test1.hdr")

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT INTERFILE END:")
			d = i2d.readHeader("test2.hdr")

		os.remove("test.hdr")
		os.remove("test1.hdr")
		os.remove("test2.hdr")

	def test_recognizeTypeInterfile(self):

		print("\n")

		type1 = "unsigned int"
		type2 = "int"
		type3 = "a"

		bytes1 = 8
		bytes2 = -1
		bytes3 = "error"

		test = lambda t,b: i2d.recognizeTypeInterfile(t,b)

		self.assertEqual(test(bytes1,type1),np.uint64)
		self.assertEqual(test(bytes1,type2),np.int64)

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT TYPE:")
			x = test(bytes1,type3)

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT BYTES PER PIXEL NUMBER:")
			x = test(bytes2,type1)

		with self.assertRaises(ValueError):
			print("TESTING INCORRECT BYTES PER PIXEL INPUT:")
			x = test(bytes3,type1)

	def test_parseHead(self):

		head_dict = {}

		with self.assertRaises(ValueError):
			print("TESTING EMPTY DICTIONARY:")
			x = i2d.parseHead(head_dict)


		#args_keys = ["in_file","out_file","width","height","frames","bytes_per_pix","is_signed","byte_order"]


		head_dict["patient name"] = "x"	
		head_dict["matrix size [1]"] = 2	
		head_dict["matrix size [2]"] = 2	
		head_dict["matrix size [3]"] = 2	
		head_dict["number of bytes per pixel"] = 8	
		head_dict["number format"]	= "unsigned"
		head_dict["imagedata byte order"] = "littlesomething"

		print("TESTING DICTIONARY WITH NO KEYS:")
		x = i2d.parseHead(head_dict)
		self.assertEqual(x["width"] , "")
		self.assertEqual(x["in_file"], "")

		head_dict["name of data file"] = "x"
		head_dict["number of dimensions"] = 3

		x = i2d.parseHead(head_dict)

		self.assertEqual(x["out_file"], "x")
		self.assertEqual(x["width"], 2)
		self.assertEqual(x["is_signed"], False)
		self.assertEqual(x["byte_order"], "little")

def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()


