import sys
from os import path
from time import localtime, strftime
from configparser import ConfigParser
from colorama import init
import base64


def decode_b64(msg: str, dst: str):
    __f = open(dst, 'wb')
    __f.write(base64.b64decode(msg))
    __f.close()


def jis_2_utf(jis: str, utf: str):
    jis_xml = open(jis, 'r', encoding='cp932')
    jis_data = jis_xml.readlines()
    jis_xml.close()

    utf_xml = open(utf, 'w', encoding='utf-8')
    utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
    jis_data.pop(0)
    for line in jis_data:
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
init(autoreset=True)


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


# Read config.cfg
class Config:

    def __init__(self):
        self.cfg = ConfigParser()
        self.path = local_dir + '/config.cfg'
        if not path.exists(self.path):
            timber.warning('config.cfg not found, the program will try to generate a new one.\n'
                           'Press enter to continue.')
            self.create()
            sys.exit(1)

        self.map_size, self.card_num, self.db_dir, self.game_dir, self.output, self.skin_name, self.is_init = \
            self.read()

        self.validity_check()

    def create(self):
        __cfg = open(self.path, 'w', encoding='utf-8')
        __cfg.write(
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
            '# name of skin, default as "gen6" (actually there is no other choice)\n'
            'skin name=gen6\n'
            '\n'
            '[Init]\n'
            '# If you have updated your game, set the value to "False" or "0"\n'
            'is initialized=False\n'
        )
        __cfg.close()

    def read(self):
        self.cfg.read(self.path, encoding='utf-8')

        map_size = self.cfg.getint('Search', 'map size')
        card_num = self.cfg.get('Search', 'card num')
        db_dir = self.cfg.get('Directory', 'db path').replace('\\', '/')
        game_dir = self.cfg.get('Directory', 'game path').replace('\\', '/')
        output = self.cfg.get('Directory', 'output path').replace('\\', '/')
        skin_name = self.cfg.get('Plot', 'skin name')
        is_init = self.cfg.getboolean('Init', 'is initialized')

        timber.info('config.cfg load complete.\n\n'
                    'map size  :%d\ncard num  :%s\ndb dir    :%s\ngame dir  :%s\noutput    :%s\n'
                    'skin name :%s\nis init   :%s\n'
                    % (map_size, card_num, db_dir, game_dir, output, skin_name, is_init is not None))

        return map_size, card_num, db_dir, game_dir, output, skin_name, is_init

    def validity_check(self):
        path_list = self.cfg.items('Directory')
        for data_path in path_list:
            __key, __value = data_path
            if not path.exists(__value):
                timber.error('%s not found, please check your file directory.' % __key)

    def add_init_sign(self):
        self.cfg.set('Init', 'is initialized', 'True')
        self.cfg.write(open(self.path, 'w'))


cfg = Config()
