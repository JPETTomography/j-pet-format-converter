#Reader module tests
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import unittest
from pathlib import Path
import os

import sys
sys.path.insert(1,'..')

#[NOTE] pylint throws an error but it works
import converter.reader as rd
from converter.exceptions import InterfileInvalidHeaderException, InterfileInvalidValueException
from converter.settings import TEST_DIR

class ReaderTest(unittest.TestCase):

    '''Test if header import (reader.py:13) works'''
    def test_header_import(self):
    
        #Header file content setup

        correct = """!INTERFILE := 
process status := 
!matrix size [3] := 200


!number format := short float
!END OF INTERFILE :="""

        incorrect1 = """!INTERFILE := 
!matrix size [3] := 200
"""

        incorrect2 = """ 
!matrix size [3] := 200
!END OF INTERFILE := """

        incorrect3 = """!INTERFILE := 
process status := 
!matrix size [3] := 200

 

!number format := short float
!END OF INTERFILE :="""

        #Header file path setup

        p_cor = Path(TEST_DIR+"/cor.hdr") #correct file
        p_nofile = Path(TEST_DIR+"/a") #no file
        p_incor1 = Path(TEST_DIR+"/incor1.hdr") #no starting tag
        p_incor2 = Path(TEST_DIR+"/incor2.hdr") #no ending tag
        p_incor3 = Path(TEST_DIR+"/incor3.hdr") #invalid formating

        #Header file creation

        paths = [p_cor, p_incor1, p_incor2, p_incor3]
        content = [correct, incorrect1, incorrect2, incorrect3]

        for i in range(4):
            with open(paths[i],"w") as f:
                f.write(content[i])

        #Test if methods outputs correct data from correct input

        print("[TEST] CORRECT HEADER TEST")
        dict = rd.header_import(path= p_cor)
        self.assertEqual(dict["process status"],
                        "",
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")
        self.assertEqual(dict["matrix size [3]"],
                        200,
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")
        self.assertEqual(dict["number format"],
                        "short float",
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")

        #Test if method throws InterfileInvalidHeaderException

        print("[TEST] INCORRECT HEADER TESTS")
        inv_header = [p_nofile, p_incor1, p_incor2]

        for invalid in inv_header:
            with self.assertRaises(InterfileInvalidHeaderException):
                dict = rd.header_import(path= invalid)
        
        #Test if method throws InterfileInvalidValueException

        #! commented out because i can't see why incorr3 has incorrect formatting
        #with self.assertRaises(InterfileInvalidValueException):
        #    dict = rd.header_import(path= p_incor3)


    def test_read_image(self):
        pass

def run_tests():

    #make temporary directory for test files
    if not Path.exists(Path("/tmp/i2d_test")):
        os.mkdir(TEST_DIR)

    #run tests
    unittest.main()

if __name__ == '__main__':
	run_tests()