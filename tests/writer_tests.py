#Writer module tests
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import unittest
from pathlib import Path
import os
import sys

import JPET-format-converter

sys.path.insert(1,'../src/converter')

from converter.exceptions import *
from converter.settings import TEST_DIR
from converter.reader import header_import
from converter.writer import write_dicom

class WriterTests(unittest.TestCase):

    def test_write_dicom(self): #test emulates conversion process

        arg_dict = header_import(path= Path("/home/kruk/Code/Python/j-pet-format-converter/examples/recon_3_1_it3.hdr"))
        #[TODO] separate adding meta data and image data to Dicom dataset from write_dicom
        write_dicom(arg_dict,{})

def run_tests():

    #make temporary directory for test files
    if not Path.exists(Path("/tmp/i2d_test")):
        os.mkdir(TEST_DIR)

    #run tests
    unittest.main()

if __name__ == '__main__':
	run_tests()