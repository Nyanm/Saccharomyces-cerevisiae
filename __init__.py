"""
pyinstaller -i sjf.ico -F main.py
"""
from main import SDVX
from cfg_read import Timber
from traceback import format_exc

timber = Timber('__init__.py')

if __name__ == '__main__':
    try:
        sdvx = SDVX()
        while True:
            sdvx.input_handler()
    except Exception:
        timber.error('Fatal error occurs, please report the following message to developer.\n\n%s\n'
                     % format_exc())
