#Writer module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
import shutil

from converter.reader import _read_interfile_header
from converter.writer import write_dicom


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


class TestWriter:

    def test_write_dicom(self, temp_directory): #test emulates conversion process

        file_name = "example_1.hdr"
        source_path = Path(f"examples/{file_name}")
        test_path = Path(temp_directory / file_name)

        # Copy example interfile to temp test directory
        shutil.copy(source_path, test_path)

        arg_dict = _read_interfile_header(path=test_path)

        write_dicom(arg_dict, {})
