#Reader module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
import inspect

import pytest

import converter.reader as rd
from converter.exceptions import InterfileInvalidHeaderException


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


class TestReader:

    def test_interfile_header_import_ok(self, temp_directory):
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


        #Header file path setup

        p_cor = Path(temp_directory / "cor.hdr") #correct file

        #Header file creation

        paths = [p_cor,]
        content = [correct,]

        for path, file_data in zip(paths, content):
            with open(path, "w") as f:
                f.write(file_data)

        #Test if methods outputs correct data from correct input

        res = rd._read_interfile_header(path=p_cor)

        assert res["process status"] == "", "ERROR! WRONG VALUE BINDED TO KEY"
        assert res["matrix size [3]"] == 200, "ERROR! WRONG VALUE BINDED TO KEY"
        assert res["number format"] == "short float", "ERROR! WRONG VALUE BINDED TO KEY"


    def test_interfile_header_import_fail(self, temp_directory):
        """
            Test if header import works
        """
        #Header file content setup
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

        #Header file path setup

        p_nofile = Path(temp_directory / "a") #no file
        p_incor1 = Path(temp_directory / "incor1.hdr") #no starting tag
        p_incor2 = Path(temp_directory / "incor2.hdr") #no ending tag

        #Header file creation

        paths = [p_incor1, p_incor2,]
        content = [incorrect1, incorrect2,]

        for path, file_data in zip(paths, content):
            with open(path, "w") as f:
                f.write(file_data)

        #Test if method throws InterfileInvalidHeaderException

        inv_header = [p_nofile, p_incor1, p_incor2]

        for invalid in inv_header:
            with pytest.raises(InterfileInvalidHeaderException):
                rd._read_interfile_header(path= invalid)

    def test_read_interfile_image(self, temp_directory):
        pass
