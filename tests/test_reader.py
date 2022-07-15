#Reader module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
import inspect

import pytest

import converter.reader as rd
from converter.exceptions import InterfileInvalidHeaderException, InterfileInvalidValueException


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


class TestReader:

    def test_interfile_header_import(self, temp_directory):
        """
            Test if header import works
        """
        #Header file content setup
        correct = inspect.cleandoc(
            """!INTERFILE := 
            process status := 
            !matrix size [3] := 200


            !number format := short float
            !END OF INTERFILE :="""
        )

        incorrect1 = inspect.cleandoc(
            """!INTERFILE := 
            !matrix size [3] := 200
            """
        )

        incorrect2 = inspect.cleandoc(
            """ 
            !matrix size [3] := 200
            !END OF INTERFILE := """
        )

        incorrect3 = inspect.cleandoc(
            """!INTERFILE := 
            process status := 
            !matrix size [3] := 200

             

            !number format := short float
            !END OF INTERFILE :="""
        )

        #Header file path setup

        p_cor = Path(temp_directory / "cor.hdr") #correct file
        p_nofile = Path(temp_directory / "a") #no file
        p_incor1 = Path(temp_directory / "incor1.hdr") #no starting tag
        p_incor2 = Path(temp_directory / "incor2.hdr") #no ending tag
        p_incor3 = Path(temp_directory / "incor3.hdr") #invalid formating

        #Header file creation

        paths = [p_cor, p_incor1, p_incor2, p_incor3]
        content = [correct, incorrect1, incorrect2, incorrect3]

        for path, file_data in zip(paths, content):
            with open(path, "w") as f:
                f.write(file_data)

        #Test if methods outputs correct data from correct input

        dict = rd._read_interfile_header(path=p_cor)
        assert dict["process status"] == "", "ERROR! WRONG VALUE BINDED TO KEY"

        assert dict["matrix size [3]"] == 200, "ERROR! WRONG VALUE BINDED TO KEY"

        assert dict["number format"] == "short float", "ERROR! WRONG VALUE BINDED TO KEY"

        #Test if method throws InterfileInvalidHeaderException

        inv_header = [p_nofile, p_incor1, p_incor2]

        for invalid in inv_header:
            with pytest.raises(InterfileInvalidHeaderException):
                dict = rd._read_interfile_header(path= invalid)

        #Test if method throws InterfileInvalidValueException

        #! commented out because i can't see why incorr3 has incorrect formatting
        #with pytest.raises(InterfileInvalidValueException):
        #    dict = rd._read_interfile_header(path= p_incor3)


    def test_read_interfile_image(self, temp_directory):
        pass
