#Converter API
#Author: Mateusz Kruk
#Version: 2.0
#E-mail: mateusz64.kruk@student.uj.edu.pl

import argparse
import sys
from pathlib import Path

import reader as rd
import writer as wr
from exceptions import *

version_str = "Version 2.0"

def convert_intefile(input: str, output = None, directory = None, meta = ()) -> None:
    try:
        p = Path(input)
        header_dict = rd.header_import(p)
        if directory is not None:
            header_dict['output path'] = directory + '/'
        else:
            header_dict['output path'] = './'
        if output is not None:
            header_dict['output path'] += output
        else:
            header_dict['output path'] += input.split('/')[-1].replace('.hdr','.dcm')
        wr.write_dicom(header_dict, meta)
    except:
        print("[ERROR]",sys.exc_info()[0])

def main():

    parser = argparse.ArgumentParser(
    description='This is a interfile to dicom converter created by Mateusz Kruk and Rafal Maselek.',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('in_file', help='input interfile header/headers', type=str, nargs="+")
    parser.add_argument('-o','--output_file', help='output file name/names', type=str, nargs="+", default=[])
    parser.add_argument('-d','--directory', help='output directory', type=str, default='.')
    parser.add_argument('-v', '--version', action='version', version=version_str)
    parser.add_argument('-m', '--meta', help='use external meta data in JSON', type=str, nargs='?', default=None)

    args = parser.parse_args()
    if len(args.in_file) == len(args.output_file):
        pair_arr = zip(args.in_file,args.output_file)
    else:
        pair_arr = zip(args.in_file,[None for i in args.in_file])
    for input, output in pair_arr:
        convert_intefile(input,output,args.directory)

    print("Converted Complete")
    

if __name__ == "__main__":
    main()
