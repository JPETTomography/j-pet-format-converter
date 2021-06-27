#Reader module tests
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import unittest
from pathlib import Path
import os

import sys
sys.path.insert(1,'..')

import src.reader as rd
from src.exceptions import InterfileInvalidHeaderException, InterfileInvalidValueException

class ReaderTest(unittest.TestCase):

    '''Test if header import (reader.py:13) works'''
    def test_header_import(cls):
    
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

        p_cor = Path("/tmp/i2d_test/cor.hdr") #correct file
        p_nofile = Path("/tmp/i2d_test/a") #no file
        p_incor1 = Path("/tmp/i2d_test/incor1.hdr") #no starting tag
        p_incor2 = Path("/tmp/i2d_test/incor2.hdr") #no ending tag
        p_incor3 = Path("/tmp/i2d_test/incor3.hdr") #invalid formating

        #Header file creation

        paths = [p_cor, p_incor1, p_incor2, p_incor3]
        content = [correct, incorrect1, incorrect2, incorrect3]

        for i in range(4):
            with open(paths[i],"w") as f:
                f.write(content[i])

        #Test if methods outputs correct data from correct input

        print("[TEST] CORRECT HEADER TEST")
        dict = rd.header_import(path= p_cor)
        cls.assertEqual(dict["process status"],
                        "",
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")
        cls.assertEqual(dict["matrix size [3]"],
                        200,
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")
        cls.assertEqual(dict["number format"],
                        "short float",
                        "ERROR! WRONG VALUE BINDED TO KEY IN header_import()")

        #Test if method throws InterfileInvalidHeaderException

        print("[TEST] INCORRECT HEADER TESTS")
        inv_header = [p_nofile, p_incor1, p_incor2]

        for invalid in inv_header:
            with cls.assertRaises(InterfileInvalidHeaderException):
                dict = rd.header_import(path= invalid)
        
        #Test if method throws InterfileInvalidValueException

        with cls.assertRaises(InterfileInvalidValueException):
                dict = rd.header_import(path= p_incor3)

def run_tests():

    #make temporary directory for test files
    try:
        os.mkdir("/tmp/i2d_test")
    except Exception:
        pass

    #run tests
    unittest.main()

if __name__ == '__main__':
	run_tests()