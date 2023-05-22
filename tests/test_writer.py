#Writer module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import logging
import shutil
from pathlib import Path

from pytest import mark

from converter.reader import interfile_header_import, read_json_meta
from converter.writer import write_dicom

from .conftest import test_params

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


class TestWriter:

    @mark.order(1)
    @mark.dependency()
    @mark.parametrize("img_type", test_params)
    def test_write_dicom_ct_ok(self, img_type, data_directory):

        file_name = f"example_{img_type.lower()}.hdr"
        metafile_name = f"metadata_{img_type.lower()}.json"
        source_path = data_directory / "inputs/interfiles"
        metafile_path = Path(f"tests/inputs/{metafile_name}")
        test_path = data_directory / file_name
        output_path = data_directory / "outputs" / file_name.replace('.hdr','')

        # Copy example interfile to temp test directory
        shutil.copytree(source_path, data_directory, dirs_exist_ok=True)

        interfile_header = interfile_header_import(path=test_path)

        metadata = read_json_meta(metafile_path, img_type)

        write_dicom(interfile_header, metadata, output_path, extended_format=False)
