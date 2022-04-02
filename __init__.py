"""
pyinstaller -i sjf.ico -F __init__.py
"""
import sys

from app import SDVX
from utli.logger import timber
from traceback import format_exc

if __name__ == '__main__':
    try:
        sdvx = SDVX()
        while True:
            sdvx.input_handler()
    except Exception:
        timber.error('Fatal error occurs, please report the following message to developer.\n%s'
                     % format_exc())
        sys.exit(1)
