import parse.sql_handler as sh

from util.logger import timber
from util.struct import MusicData, LevelData, AkaData, SearchData
from util.cfg import Config
from util.local import local_dir

from value.project_cfg import LOWEST_VERSION

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
        self._data_dir = cfg.gameDir + '/data'
        timber.debug(f'Get ea3-config.xml path [{ea3_path}]')
        timber.debug(f'Get ./contents/data directory [{self._data_dir}]')

        # validity check
        if not path.exists(ea3_path) or not path.exists(self._data_dir):
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

        local_db_path = local_data_dir + '/music.sqlite3'
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
        try:
            self._cur.execute(sh.INIT_QUERY_MASTER)  # get number of table 'METADATA'
            cnt = self._cur.fetchall()[0][0]
            if cnt != 1:  # the critical table 'METADATA' is missing
                return False
            self._cur.execute(sh.QUERY_METADATA)
            metadata = self._cur.fetchall()

        except sqlite3.Error:  # anything crashes the query
            return False

    def _read_database(self):
        pass

    def _update(self):
        timber.info('database will be updated due to the force option or outdated version')
        self._parse_music_db()
        self._parse_aka_db()

    def _generate_metadata(self):
        pass

    def _parse_music_db(self):
        jis_path = self._data_dir + '/others/music_db.xml'
        timber.debug(f'Get music_db.xml path [{jis_path}]')
        if not path.exists(jis_path):
            timber.error('Path of ./contents/data/others/music_db.xml is unavailable, please check your file directory.'
                         ' File paths were given in log file(timber.log).')
            input('Press enter to continue')
            exit(1)

        # convert cp932 to utf-8
        # 我感谢日本人全家
        jis_xml = open(jis_path, 'r', encoding='cp932')
        jis_data = jis_xml.readlines()
        jis_xml.close()

        utf_path = self._data_dir + '/music_db.xml'
        utf_xml = open(utf_path, 'w', encoding='utf-8')
        utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
        jis_data.pop(0)
        for line in jis_data:
            utf_xml.write(line)
        utf_xml.close()

        # get music information from xml
        tree = parse(utf_path)
        root = tree.getroot()

    def _parse_aka_db(self):
        aka_path = self._data_dir + '/others/akaname_parts.xml'
        timber.debug(f'Get akaname_parts.xml path [{aka_path}]')
        if not path.exists(aka_path):
            timber.error('Path of ./contents/data/others/akaname_parts.xml is unavailable, '
                         'please check your file directory.'
                         'File paths were given in log file(timber.log).')
            input('Press enter to continue')
            exit(1)

    def _generate_search_db(self):
        pass
