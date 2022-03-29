"""
pyinstaller -i sjf.ico -F __init__.py
"""
from main.main import SDVX
from main.logger import timber
from traceback import format_exc

if __name__ == '__main__':
    try:
        sdvx = SDVX()
        while True:
            sdvx.input_handler()
    except Exception:
        timber.error('Fatal error occurs, please report the following message to developer.\n\n%s\n'
                     % format_exc())
