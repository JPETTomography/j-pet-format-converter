#Reader module
#Author: Mateusz Kruk
#E-mail: mateusz64.kruk@student.uj.edu.pl

import sys
sys.path.insert(1,'..')

from pathlib import Path

from src.exceptions import *
from src.settings import CASToR_VERSION

def header_import(path: Path):

    meta_dict = {}

    try:
        with open(path,"r") as header:
            
            line = header.readline()
            if line != "!INTERFILE := \n":
                raise InterfileInvalidHeaderException('invalid start header format')
			
            bufor = header.readlines()

            for line in bufor:
                line = line.strip('!\n')
                line = line.split(' :=')
                if line[0] != '':
                    if 'end' in line[0].lower():
                        return meta_dict
                    elif 'general' not in line[0].lower():
                        try:
                            meta_dict[line[0]] = int(line[1])
                        except ValueError:
                            if line[1][0] == '':
                                meta_dict[line[0]] = line[1]
                            else:
                                meta_dict[line[0]] = line[1][1:]
                        except Exception:
                            raise InterfileInvalidValueException('invalid header format')


        raise InterfileInvalidHeaderException('invalid end header format')

    except FileNotFoundError:
        print("[ERROR] file not found !")
        raise InterfileInvalidHeaderException

    except Exception as e:
        x = e.args
        print("[ERROR]",x[0],"!")
        raise e
