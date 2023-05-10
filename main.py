# Converter API
#Author: Mateusz Kruk, Rafal Mozdzonek

import argparse
import logging
from pathlib import Path

import converter.reader as rd
import converter.writer as wr

LOGGER = logging.getLogger(__name__)


version_str = "Version 2.0"

def convert_intefile_to_dicom(
    input_path: str,
    meta_path: str,
    output=None,
    directory=None,
    extended_format=False
) -> None:
    p = Path(input_path)
    header_obj = rd.interfile_header_import(p)
    metadata = rd.read_json_meta(Path(meta_path), header_obj.modality)

    if directory is not None:
        output_path = directory + '/'
    else:
        output_path = './'

    if output is not None:
        output_path += output
    else:
        output_path += input_path.split('/')[-1].replace(
            '.hdr', '.dcm' if extended_format else ''
        )

    wr.write_dicom(
        header_obj,
        metadata,
        output_path=Path(output_path),
        extended_format=extended_format
    )

def main():

    parser = argparse.ArgumentParser(
        description='This is a interfile to dicom converter created by the J-PET collaboration.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--input_file',
        help='input interfile header',
        type=str,
        required=True
    )
    parser.add_argument(
        '-m',
        '--meta_file',
        help='path to external meta data in JSON',
        type=str,
        nargs='?',
        required=True
    )
    parser.add_argument(
        '-o', '--output_file',
        help='output file name',
        type=str,
        nargs="?",
        default=None
    )
    parser.add_argument('-d','--directory', help='output directory', type=str, default='.')
    parser.add_argument('-v', '--version', action='version', version=version_str)

    parser.add_argument('--extended', action='store_true')
    parser.add_argument('--no-extended', dest='extended', action='store_false')
    parser.set_defaults(extended=False)

    args = parser.parse_args()
    convert_intefile_to_dicom(
        args.input_file,
        args.meta_file,
        args.output_file,
        args.directory,
        extended_format=args.extended
    )

    LOGGER.info("Convertion Completed")


if __name__ == "__main__":
    main()
