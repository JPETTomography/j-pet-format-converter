import interfile2DICOM as i2d
import unittest

class HeaderTest(unittest.TestCase):

	def readHeader_test(self):

		correct_text = "!INTERFILE := \n!test key := test_valu\n!END OF INTERFILE := "
		error1_text = "test"
		error2_text = "!INTERFILE := \n test"

		f = open("test.hdr","wb")
		f.write(correct_text)
		f.close()

		try:
			d = readHeader("test.hdr")
		except SystemExit:
			self.fail("ERROR! readHeader() RAISED AN ERROR WITH CORRECT FILE")

		if d['test key'] != 'test_value':
			self.fail("ERROR! WRONG VALUE BINDED TO KEY IN readHeader()")

		f = open("test.hdr","wb")
		f.write(error1_text)
		f.close()

		try:
			d = readHeader("test.hdr")
			self.fail("ERROR! readHeader() DID NOT RAISED AN ERROR WITH INCORRECT FILE")
		except SystemExit:
			print("TASK FAILED SUCCESSFULLY")

		f = open("test.hdr","wb")
		f.write(error2_text)
		f.close()

		try:
			d = readHeader("test.hdr")
			self.fail("ERROR! readHeader() DID NOT RAISED AN ERROR WITH INCORRECT FILE")
		except SystemExit:
			print("TASK FAILED SUCCESSFULLY")


def run_tests():
    unittest.main()

if __name__ == '__main__':
    run_tests()


