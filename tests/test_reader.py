#Reader module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import inspect
import logging
import numpy as np
import math
import os
from pathlib import Path

import pydicom
import pytest
from pytest import mark

import converter.reader as rd
from converter.exceptions import InterfileInvalidHeaderException

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)
LOGGER.setLevel(logging.DEBUG)


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
                rd._read_interfile_header(path=invalid)

    @mark.parametrize("img_type", ["PT"])
    def test_read_interfile_image(self, img_type, data_directory):
        img_type = img_type.lower()

        test_dir = data_directory / Path(f"dicoms/example_{img_type}/")
        test_files = os.listdir(test_dir)
        test_slices = [pydicom.dcmread(os.path.join(test_dir, file)) for file in test_files]
        test_slices = sort_slices(test_slices)

        reference_dir = data_directory / Path(f"dicoms/reference_{img_type}/")
        reference_files = os.listdir(reference_dir)
        reference_slices = [
            pydicom.dcmread(os.path.join(reference_dir, file)) for file in reference_files
        ]
        reference_slices = sort_slices(reference_slices)

        for test_slice, reference_slice in zip(test_slices, reference_slices):
            test_columns = test_slice.Columns
            test_rows = test_slice.Rows
            test_pixel_data = test_slice.PixelData

            test_image_position_patient = test_slice.ImagePositionPatient
            test_instance_number = test_slice.InstanceNumber
            test_image_index = test_slice.ImageIndex

            reference_columns = reference_slice.Columns
            reference_rows = reference_slice.Rows
            reference_pixel_data = reference_slice.PixelData

            reference_image_position_patient = reference_slice.ImagePositionPatient
            reference_instance_number = reference_slice.InstanceNumber
            reference_image_index = reference_slice.ImageIndex

            epsilon_x = float(reference_slice.PixelSpacing[0])
            epsilon_y = float(reference_slice.PixelSpacing[1])
            epsilon_z = float(reference_slice.SliceThickness)

            assert test_rows == reference_rows
            assert test_columns == reference_columns
            assert test_pixel_data == reference_pixel_data

            assert math.isclose(
                test_image_position_patient[0],
                reference_image_position_patient[0],
                rel_tol=epsilon_x
            )
            assert math.isclose(
                test_image_position_patient[1],
                reference_image_position_patient[1],
                rel_tol=epsilon_y
            )
            assert math.isclose(
                test_image_position_patient[2],
                reference_image_position_patient[2],
                rel_tol=epsilon_z
            )

            assert test_instance_number == reference_instance_number
            assert test_image_index == reference_image_index

def sort_slices(slices):
    """
    Sort images (slices) slices based on ImagePositionPatient and ImageOrientationPatient.
    Based on: https://medium.com/redbrick-ai/dicom-coordinate-systems-3d-dicom-for-computer-vision-engineers-pt-1-61341d87485f
    """
    def get_slice_projections(slices):
        slice_projections = []
        for slice in slices:
            iop = np.array(slice.ImageOrientationPatient)
            ipp = np.array(slice.ImagePositionPatient)
            normal = np.cross(iop[0:3], iop[3:])
            projection = np.dot(ipp, normal)
            slice_projections += [{"d": projection, "slice": slice}]
        return slice_projections

    slice_projections = get_slice_projections(slices)
    sorted_slices = sorted(slice_projections, key=lambda i: i['d'])
    return [slice['slice'] for slice in sorted_slices]
