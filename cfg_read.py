import re
import sys
from os import path
from time import localtime, strftime
import base64


def decode_b64(msg: str, dst: str):
    __f = open(dst, 'wb')
    __f.write(base64.b64decode(msg))
    __f.close()


def jis_2_utf(jis: str, utf: str):
    jis_xml = open(jis, 'r', encoding='cp932').readlines()
    utf_xml = open(utf, 'w', encoding='utf-8')
    utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
    jis_xml.pop(0)
    for line in jis_xml:
        utf_xml.write(line)
    utf_xml.close()


# Turn off test mode when packing the program
test_mode = 1
if test_mode:
    local_dir = path.dirname(path.abspath(__file__)).replace('\\', '/')
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')

# Clean timber.log up
timber_path = local_dir + '/timber.log'
f = open(timber_path, 'w', encoding='utf-8')
f.close()


# Initialize logger
class Timber:
    def __init__(self, filename):
        self.filename = filename
        self.fmt = '[%s][%s][%s]:%s\n'

    def write(self, msg: str, level: str):
        logger = open(timber_path, 'a', encoding='utf-8')
        logger.write(self.fmt % (strftime("%H:%M:%S", localtime()), self.filename, level, msg))
        logger.close()

    def info(self, msg: str):
        self.write(msg, 'Info')

    def info_show(self, msg: str):
        print('\33[32m[Info] %s\33[0m' % msg)
        self.write(msg, 'Info')

    def info_clog(self, msg: str):
        input('\33[32m[Info] %s\33[0m' % msg)
        self.write(msg, 'Info')

    def warning(self, msg: str):
        input('\33[33m[Warning] %s\33[0m' % msg)
        self.write(msg, 'Warning')

    def error(self, msg: str):
        input('\33[31m[Error] %s\33[0m' % msg)
        self.write(msg, 'Error')
        sys.exit(1)


timber = Timber('cfg_read.py')
timber.info('test mode=%s' % test_mode)  # Initial logging

# Read config.txt
cfg_path = local_dir + '/config.txt'
try:
    __raw_file = open(cfg_path, 'r')
except FileNotFoundError:
    timber.warning('config.txt not found, the program will try to generate a new one.\nPress enter to continue.')
    cfg = open(cfg_path, 'w', encoding='utf-8')
    cfg.write(
        '[Search]\n'
        '# Range of mid, default as 2000\n'
        'map size=2000\n'
        '# User\'s card number in asphyxia\'s website (or database), a 16 bit long hex number sequence\n'
        'card num=\n'
        '\n'
        '[Directory]\n'
        '# Directory of sdvx@asphyxia\'s database\n'        
        '# eg. db path=C:\\MUG\\asphyxia-core\\savedata\\sdvx@asphyxia.db\n'
        'db path=\n'
        '\n'
        '# Directory of sdvx HDD data\n'
        '# eg. game path=C:\\MUG\\SDVX6\\KFC-2021051802\\contents\\data\n'
        'game path=\n'
        '\n'
        '# Directory where outputs pictures\n'
        'output path=\n'
        '[Plot]\n'
        '# name of skin, default as "gen6"\n'
        'skin name=gen6\n'
        '\n'
        '[Init]\n'
        '# If you have updated your game, delete the following line\n'
    )
    cfg.close()
    sys.exit(1)

cfg_data = ''
for __line in __raw_file.readlines():
    if __line[0] == '#':
        continue
    cfg_data += __line
__raw_file.close()

# Data cleaning
get_map_size = re.compile(r'map size+[^\n]*')
get_card_cfg = re.compile(r'card num+[^\n]*')
get_db_dir = re.compile(r'db path+[^\n]*')
get_game_dir = re.compile(r'game path+[^\n]*')
get_output = re.compile(r'output path+[^\n]*')
get_skin = re.compile(r'skin name+[^\n]*')
get_init_stat = re.compile(r'is initialized+[^\n]*')

map_size = int(get_map_size.search(cfg_data).group()[9:])
card_num = get_card_cfg.search(cfg_data).group()[9:]
db_dir = get_db_dir.search(cfg_data).group()[8:].replace('\\', '/')
game_dir = get_game_dir.search(cfg_data).group()[10:].replace('\\', '/')
output = get_output.search(cfg_data).group()[12:].replace('\\', '/')
skin_name = get_skin.search(cfg_data).group()[10:]
is_init = get_init_stat.search(cfg_data)

timber.info('config.txt load complete.\n\n'
            'map size  :%d\ncard num  :%s\ndb dir    :%s\ngame dir  :%s\noutput    :%s\nskin name :%s\nis init   :%s\n'
            % (map_size, card_num, db_dir, game_dir, output, skin_name, is_init is not None))

# Validity check
if not path.exists(db_dir):
    timber.error('sdvx@asphyxia.db not found, please check your file directory.')
    sys.exit(1)
if not path.exists(game_dir):
    timber.error(r'KFC-**********\contents\data not found, please check your file directory.')
    sys.exit(1)
if not path.exists(output):
    timber.error('Output folder not found, please check your file directory.')
    sys.exit(1)
