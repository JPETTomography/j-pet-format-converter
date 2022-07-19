#Converter API
#Author: Mateusz Kruk, Rafal Mozdzonek

import logging
import argparse
import sys
from pathlib import Path

import converter.reader as rd
import converter.writer as wr
from models.metadata import MetaFile


LOGGER = logging.getLogger(__name__)


version_str = "Version 2.0"

def convert_intefile_to_dicom(input: str, output=None, directory=None, meta=None) -> None:
    try:
        p = Path(input)
        header_obj = rd.interfile_header_import(p)
        if meta:
            metadata = rd.read_json_meta(Path(meta))
        else:
            metadata = None

        if directory is not None:
            output_path = directory + '/'
        else:
            output_path = './'
        if output is not None:
            output_path += output
        else:
            output_path += input.split('/')[-1].replace('.hdr','.dcm')
        wr.write_dicom(
            header_obj,
            metadata,
            output_path=Path(input.split('/')[-1].replace('.hdr','.dcm'))
        )
    except:
        raise
        # LOGGER.error(sys.exc_info()[1])

def main():

    parser = argparse.ArgumentParser(
        description='This is a interfile to dicom converter created by the J-PET collaboration.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_file', help='input interfile header', type=str, nargs="?")
    parser.add_argument(
        '-o', '--output_file',
        help='output file name',
        type=str,
        nargs="?",
        default=None
    )
    parser.add_argument('-d','--directory', help='output directory', type=str, default='.')
    parser.add_argument('-v', '--version', action='version', version=version_str)
    parser.add_argument(
        '-m',
        '--meta',
        help='path to external meta data in JSON',
        type=str,
        nargs='?',
        default=None
    )

    args = parser.parse_args()
    convert_intefile_to_dicom(args.input_file, args.output_file, args.directory, args.meta)


    LOGGER.info("Converted Complete")


if __name__ == "__main__":
    main()
