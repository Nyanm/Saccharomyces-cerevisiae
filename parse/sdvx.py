from util.logger import timber
from util.struct import MusicData, LevelData, AkaData, SearchData
from util.cfg import Config
from util.local import local_dir

from os import path, mkdir
import sqlite3

from xml.etree.cElementTree import parse


class SdvxParser:
    """
    TODO: ADD A BRIEF
    """

    def __init__(self, cfg: Config):
        # public zone
        self.musicDataMap = []
        self.akaDataMap = []
        self.searchDataMap = []
        self.mapSize: int = 2500

        # private variables
        ea3_path = cfg.gameDir + '/prop/ea3-config.xml'
        data_dir = cfg.gameDir + '/data'
        timber.debug(f'Get ea3-config.xml path [{ea3_path}]')
        timber.debug(f'Get ./contents/data directory [{data_dir}]')

        # validity check
        if not path.exists(ea3_path) or not path.exists(data_dir):
            timber.error('Path of ea3-config or ./contents/data is unavailable, please check your file directory. '
                         'File paths were given in log file(timber.log).')
            input('Press enter to continue')
            exit(1)

        # get game version code
        tree = parse(ea3_path)
        root = tree.getroot()
        self._game_version = int(root[1][4].text)
        timber.debug(f'Sound Voltex game version {self._game_version}')

        # database validity check
        local_data_dir = local_dir + '/data'
        if not path.exists(local_data_dir):
            mkdir(local_data_dir)

        local_db_path = local_data_dir + '/music.db'
        database = sqlite3.connect(local_db_path)
        self._cur = database.cursor()
        if cfg.forceInit:
            timber.info('Force update enabled')
            self._update()
        elif not self._update_check():
            self._update()

        # load data from sqlite database
        self._read_database()
        self._cur.close()
        timber.debug('SDVX data loaded')

    def _update_check(self) -> bool:
        pass

    def _read_database(self):
        pass

    def _update(self):
        pass

    def _generate_metadata(self):
        pass

    def _parse_music_db(self):
        pass

    def _parse_aka_db(self):
        pass

    def _generate_search_db(self):
        pass
