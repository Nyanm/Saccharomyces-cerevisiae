import sys
from os import path, mkdir
from time import localtime, strftime
from configparser import ConfigParser


print('More information at https://github.com/Nyanm/Saccharomyces-cerevisiae')


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
        print('[Info]''%s' % msg)
        self.write(msg, 'Info')

    def info_clog(self, msg: str):
        input('[Info]''%s' % msg)
        self.write(msg, 'Info')

    def warning(self, msg: str):
        input('[Warning]''%s' % msg)
        self.write(msg, 'Warning')

    def error(self, msg: str):
        input('[Error]''%s' % msg)
        self.write(msg, 'Error')
        sys.exit(1)


timber = Timber('cfg_read.py')
timber.info('test mode=%s' % test_mode)  # Initial logging


# Read config.cfg
class Config:
    # TODO: ADD "LANGUAGE" OPTION

    def __init__(self):
        self.cfg = ConfigParser()
        self.path = local_dir + '/config.cfg'
        if not path.exists(self.path):
            self.create()
            timber.error('config.cfg not found, the program will try to generate a new one.\n'
                         'Press enter to continue.')

        self.map_size, self.card_num, self.db_dir, self.game_dir, self.output, self.skin_name, self.is_init, self.version = self.read()
        self.validity_check()

    def create(self):
        __cfg = open(self.path, 'w', encoding='utf-8')
        __cfg.write(
            '[Search]\n'
            '# Range of mid, default as 2000\n'
            'map size = 2000\n\n'
            '# User\'s card number in asphyxia\'s website (or database), a 16 bit long hex number sequence\n'
            'card num = \n\n'
            '\n[Directory]\n'
            '# Directory of sdvx@asphyxia\'s database\n'
            '# eg. db path = C:\\MUG\\asphyxia-core\\savedata\\sdvx@asphyxia.db\n'
            'db path = \n\n'
            '# Directory of sdvx HDD data\n'
            '# eg. game path = C:\\MUG\\SDVX6\\KFC-2021051802\\contents\\data\n'
            'game path = \n\n'
            '# Directory where outputs pictures\n'
            'output path = \n\n'
            '\n[Plot]\n'
            '# name of skin, default as "gen6" (actually there is no other choice)\n'
            'skin name = gen6\n\n'
            '\n[Init]\n'
            '# If you want to update manually, set the value to "False" or "0"\n'
            'is initialized = False\n\n'
            '# Current game version in ea3-config, you can leave it as "00000000", it will be filled automatically.\n'
            'version = 0000000000\n'
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
        version = self.cfg.getint('Init', 'version')

        timber.info('config.cfg load complete.\n\n'
                    'map size  :%d\ncard num  :%s\ndb dir    :%s\ngame dir  :%s\noutput    :%s\n'
                    'skin name :%s\nis init   :%s\nversion   :%d\n'
                    % (map_size, card_num, db_dir, game_dir, output, skin_name, str(is_init), version))

        return map_size, card_num, db_dir, game_dir, output, skin_name, is_init, version

    def validity_check(self):
        path_list = self.cfg.items('Directory')
        for data_path in path_list:
            __key, __value = data_path
            if not path.exists(__value):
                if __key == 'output path':
                    timber.warning('output path not found, the program will try to make one.')
                    mkdir(__value)
                else:
                    timber.error('%s not found, please check your file directory.' % __key)

    def set_init_sign(self, set_bool: bool = True):
        self.cfg.set('Init', 'is initialized', str(set_bool))
        self.cfg.write(open(self.path, 'w'))

    def set_version(self, version: int):
        self.cfg.set('Init', 'version', str(version))
        self.cfg.write(open(self.path, 'w'))


cfg = Config()
