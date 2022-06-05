from os import mkdir, path
from configparser import ConfigParser
import sys

from .logger import timber
from .local import local_dir


class Config:
    """
    Config is the base configuration class of whole project, which provides the very rudimentary data for all other
    modules. Currently Config class has demodulated with any other part, and works as a individual module.
    It provides data in 4 parts:
    [Search] specifies user's card number.
    [Directory] collects paths of necessary files or folders.
    [Plot] stipulates how the text and pictorial results will be ploted.
    [Init] gives the user a handler to update the database manually.
    """

    def __init__(self):
        self._cfg = ConfigParser()
        self._path = local_dir + '/config.cfg'

        # may be the first start
        if not path.exists(self._path):
            self._create()
            input('Since this is your first start, the program will generate a configuration file.\n'
                  'Please fill it up under the instruction of itself and restart the software.\n'
                  'Press enter to continue.')
            exit(0)

        # get configuration from existing config.cfg
        self.cardNum = ''
        self.dbPath = ''
        self.gameDir = ''
        self.outputDir = ''
        self.skinName = ''
        self.language = ''
        self.forceInit = False
        self._read()

        # validity check
        path_list = self._cfg.items('Directory')
        for data_path in path_list:
            _key, _value = data_path
            if not path.exists(_value):
                if _key == 'output_dir':
                    timber.warning('output directory not found, the program will try to generate one.')
                    mkdir(_value)
                else:
                    timber.error(f'{_key} not found, please check your file directory.')
                    input('Press enter to continue.')
                    sys.exit(1)

    def _create(self):
        _cfg = open(self._path, 'w', encoding='utf-8')
        _cfg.write(
            '[Search]\n'
            '# User\'s card number in asphyxia\'s website (or database), a 16 bit long hex number sequence\n'
            'card_num = \n'
            '\n'
            '\n'
            '[Directory]\n'
            '# Path of sdvx@asphyxia\'s database\n'
            '# eg. db_path = C:\\MUG\\asphyxia-core\\savedata\\sdvx@asphyxia.db\n'
            'db_path = \n'
            '\n'
            '# Directory of sdvx HDD\n'
            '# eg. game_dir = C:\\MUG\\SDVX6\\KFC-2021051802\\contents\n'
            'game_dir = \n'
            '\n'
            '# Directory where outputs pictures. The program will generate one if leaving empty\n'
            'output_dir = \n'
            '\n'
            '\n'
            '[Plot]\n'
            '# name of skin, default as "gen6" (actually there is no other choice)\n'
            'skin_name = gen6\n'
            '# supported languages:[EN (English), ZH (Simplified Chinese)], default as EN\n'
            'language = EN\n'
            '\n'
            '\n'
            '[Init]\n'
            '# If you want to update manually, set the value to "True" or "1"\n'
            'force_init = False\n'
        )
        _cfg.close()
        timber.debug(f'Generate empty config file at [{self._path}]')

    def _read(self):
        self._cfg.read(self._path, encoding='utf-8')

        self.cardNum = self._cfg.get('Search', 'card_num')
        self.dbPath = self._cfg.get('Directory', 'db_path').replace('\\', '/')
        self.gameDir = self._cfg.get('Directory', 'game_dir').replace('\\', '/')
        self.outputDir = self._cfg.get('Directory', 'output_dir').replace('\\', '/')
        self.skinName = self._cfg.get('Plot', 'skin_name')
        self.language = self._cfg.get('Plot', 'language').upper()
        self.forceInit = self._cfg.getboolean('Init', 'force_init')

        timber.info(f'config.cfg load complete.\n'
                    f'card_num   :{self.cardNum}\n'
                    f'db_dir     :{self.dbPath}\n'
                    f'game_dir   :{self.gameDir}\n'
                    f'output_dir :{self.outputDir}\n'
                    f'skin_name  :{self.skinName}\n'
                    f'language   :{self.language}\n'
                    f'force_init :{self.forceInit}')

    def set_init_sign(self, set_bool: bool = True):
        self._cfg.set('Init', 'force_init', str(set_bool))
        self._cfg.write(open(self._path, 'w'))
