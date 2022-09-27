#Writer module tests
#Authors: Mateusz Kruk, Rafal Mozdzonek

import logging
from pathlib import Path
import shutil

from converter.reader import interfile_header_import, read_json_meta
from converter.writer import write_dicom


LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)-10s | %(filename)-20s | %(funcName)-15s | %(lineno)-5d | %(message)-50s\n"
)


class TestWriter:

    def test_write_dicom_standard_ok(self, temp_directory): #test emulates conversion process

        file_name = "example_1.hdr"
        metafile_name = "metadata.json"
        source_path = Path(f"examples/")
        metafile_path = Path(f"examples/{metafile_name}")
        test_path = Path(temp_directory / file_name)
        output_path = Path(temp_directory / file_name.replace('.hdr',''))

        # Copy example interfile to temp test directory
        shutil.copytree(source_path, temp_directory, dirs_exist_ok=True)

        interfile_header = interfile_header_import(path=test_path)

        metadata = read_json_meta(metafile_path)

        write_dicom(interfile_header, metadata, output_path, extended_format=False)
