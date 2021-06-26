"""
-------------------------------------
Reader module
-------------------------------------
Reads Interfile header files
"""

from pathlib import Path

from exceptions import *

def header_import(path: Path):
    try:
        with open(path,"r") as header:
            pass
        print("a")
    except FileNotFoundError:
        print("[ERROR] FILE NOT FOUND!")
        raise InterfileInvalidHeaderException

p = Path("sus.py")

header_import(p)