from os import mkdir, path
from configparser import ConfigParser
import sys

from xml.etree.cElementTree import parse

from .logger import timber
from .dir import local_dir

from ..update import update


# Read config.cfg
class Config:

    def __init__(self):
        self.cfg = ConfigParser()
        self.path = local_dir + '/config.cfg'
        if not path.exists(self.path):
            self._create()
            timber.error('config.cfg not found, the program will try to generate a new one.\n')
            input('Press enter to continue.')
            sys.exit(1)

        self.map_size, self.card_num, self.db_dir, self.game_dir, self.output, \
        self.skin_name, self.language, self.is_init, self.version = self._read()

        # validity check for paths
        path_list = self.cfg.items('Directory')
        for data_path in path_list:
            __key, __value = data_path
            if not path.exists(__value):
                if __key == 'output path':
                    timber.warning('output path not found, the program will try to make one.')
                    mkdir(__value)
                else:
                    timber.error('%s not found, please check your file directory.' % __key)
                    sys.exit(1)

        # update check (from version date code)
        ea3_path = '/'.join(self.game_dir.split('/')[:-1]) + '/prop/ea3-config.xml'
        tree = parse(ea3_path)
        root = tree.getroot()
        cur_ver = int(root[1][4].text)

        # update (if necessary)
        if not self.is_init:
            update.update(self)
            self._set_init_sign()
            self._set_version(cur_ver)
        elif cur_ver > self.version:
            update.update(self, game_only=True)
            self._set_version(cur_ver)

    def _create(self):
        _cfg = open(self.path, 'w', encoding='utf-8')
        _cfg.write(
            '[Search]\n'
            '# Range of mid, default as 2000\n'
            'map size = 2000\n'
            '\n'
            '# User\'s card number in asphyxia\'s website (or database), a 16 bit long hex number sequence\n'
            'card num = \n'
            '\n'
            '\n'
            '[Directory]\n'
            '# Directory of sdvx@asphyxia\'s database\n'
            '# eg. db path = C:\\MUG\\asphyxia-core\\savedata\\sdvx@asphyxia.db\n'
            'db path = \n'
            '\n'
            '# Directory of sdvx HDD data\n'
            '# eg. game path = C:\\MUG\\SDVX6\\KFC-2021051802\\contents\\data\n'
            'game path = \n'
            '\n'
            '# Directory where outputs pictures\n'
            'output path = \n'
            '\n'
            '\n'
            '[Plot]\n'
            '# name of skin, default as "gen6" (actually there is no other choice)\n'
            'skin name = gen6\n'
            '# supported languages:[EN (English), ZH (Simplified Chinese)], default as EN\n'
            'language = EN\n'
            '\n'
            '\n'
            '[Init]\n'
            '# If you want to update manually, set the value to "False" or "0"\n'
            'is initialized = False\n'
            '\n'
            '# Current game version in ea3-config, you can leave it as "00000000", it will be filled automatically.\n'
            'version = 0000000000\n'
        )
        _cfg.close()

    def _read(self):
        self.cfg.read(self.path, encoding='utf-8')

        map_size = self.cfg.getint('Search', 'map size')
        card_num = self.cfg.get('Search', 'card num')
        db_dir = self.cfg.get('Directory', 'db path').replace('\\', '/')
        game_dir = self.cfg.get('Directory', 'game path').replace('\\', '/')
        output = self.cfg.get('Directory', 'output path').replace('\\', '/')
        skin_name = self.cfg.get('Plot', 'skin name')
        language = self.cfg.get('Plot', 'language').upper()
        is_init = self.cfg.getboolean('Init', 'is initialized')
        version = self.cfg.getint('Init', 'version')

        timber.info('config.cfg load complete.\n'
                    'map size  :%d\ncard num  :%s\ndb dir    :%s\ngame dir  :%s\noutput    :%s\n'
                    'skin name :%s\nlanguage  :%s\nis init   :%s\nversion   :%d'
                    % (map_size, card_num, db_dir, game_dir, output, skin_name, language, str(is_init), version))

        return map_size, card_num, db_dir, game_dir, output, skin_name, language, is_init, version

    def _set_init_sign(self, set_bool: bool = True):
        self.cfg.set('Init', 'is initialized', str(set_bool))
        self.cfg.write(open(self.path, 'w'))

    def _set_version(self, version: int):
        self.cfg.set('Init', 'version', str(version))
        self.cfg.write(open(self.path, 'w'))


cfg = Config()
