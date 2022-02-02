import argparse
import sys
from pathlib import Path

sys.path.insert(1, '..')

import reader as rd
import writer as wr
from exceptions import *

version_str = "Version 2.0"

def convert_intefile(input: str, output = None, dir = None, meta = ()) -> None:
    try:
        p = Path(input)
        header_dict = rd.header_import(p)
        if output is not None:
            header_dict = rd.add_output_name(output)
        if dir is not None:
            header_dict = rd.add_output_dir(dir)
        wr.write_dicom(header_dict, meta)
    except:
        e = sys.exc_info()[0]
        raise e

def main():

    parser = argparse.ArgumentParser(
    description='This is a interfile to dicom converter created by Mateusz Kruk and Rafal Maselek.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', help='input interfile header/headers', type=str, nargs="+")
    parser.add_argument('-o','--output_file', help='output file name/names', type=str, default='(in_file).dcm')
    parser.add_argument('-d','--directory', help='output directory', type=str, default='.')
    parser.add_argument('-v', '--version', action='version', version=version_str)
    parser.add_argument('-m', '--meta', help='use external meta data in JSON', type=str, nargs='?', default='none')

    args = parser.parse_args()
    print(args)
    

if __name__ == "__main__":
    main()
