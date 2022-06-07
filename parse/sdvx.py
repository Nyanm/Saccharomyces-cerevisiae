from util.logger import timber
from util.struct import MusicData, AkaData, SearchData
from util.cfg import Config
from util.local import local_dir
from util.jis import amend_jis
import parse.sql_handler as sh

from value.project_cfg import LOWEST_GAME_VERSION, METADATA_VERSION, METADATA_FIX_VERSION

from os import path, mkdir
import os

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
        self.memeDataMap = []
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
        if self._game_version < LOWEST_GAME_VERSION:
            timber.error(f'Versions before {LOWEST_GAME_VERSION} are no longer supported.')
            input('Press enter to continue.')
            exit(1)
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
        database.commit()
        database.close()
        timber.debug('SDVX data loaded')

    def _update_check(self) -> bool:
        try:
            # whether the database exists
            self._cur.execute(sh.INIT_QUERY_MASTER)  # get number of table 'METADATA'
            cnt = self._cur.fetchall()[0][0]
            assert cnt == 1  # no table named 'METADATA'
            # check metadata
            self._cur.execute(sh.QUERY_METADATA)
            metadata = self._cur.fetchall()[0]
            return self._read_metadata_content(metadata)
        except AssertionError:  # anything crashes the query
            return False

    def _read_database(self):
        pass

    def _update(self):
        timber.info('database will be updated due to the force option or outdated version')
        self._parse_music_db()  # get self.musicDataMap, self.mapSize
        self._parse_aka_db()  # get self.akaDataMap
        self._parse_meme_db()  # get self.searchDataMap

        self._write_database()

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

        # get map size by traversal
        index, temp_map_size = 0, 0
        while True:
            try:
                mid = int(root[index].attrib['id'])
                temp_map_size = max(temp_map_size, mid)
                index += 1
            except IndexError:
                self.mapSize = temp_map_size
                self.musicDataMap = [MusicData() for _ in range(self.mapSize + 1)]
                break

        # fill up music data map
        index = 0
        while True:
            try:
                mid = int(root[index].attrib['id'])

                self.musicDataMap[mid].mID = mid
                self.musicDataMap[mid].name = amend_jis(root[index][0][1].text)
                self.musicDataMap[mid].nameYmgn = root[index][0][2].text
                self.musicDataMap[mid].artist = amend_jis(root[index][0][3].text)
                self.musicDataMap[mid].artistYmgn = root[index][0][4].text
                self.musicDataMap[mid].ascii = root[index][0][5].text.replace('_', ' ')
                self.musicDataMap[mid].bpmMax = int(root[index][0][6].text)
                self.musicDataMap[mid].bpmMin = int(root[index][0][7].text)
                self.musicDataMap[mid].date = int(root[index][0][8].text)
                self.musicDataMap[mid].version = int(root[index][0][13].text)
                self.musicDataMap[mid].infVer = int(root[index][0][15].text)

                diff_table = [self.musicDataMap[mid].novice, self.musicDataMap[mid].advanced,
                              self.musicDataMap[mid].exhausted, self.musicDataMap[mid].infinite,
                              self.musicDataMap[mid].maximum]
                for diff in range(5):
                    try:
                        diff_table[diff].level = int(root[index][1][diff][0].text)
                        diff_table[diff].illustrator = amend_jis(root[index][1][diff][1].text)
                        diff_table[diff].effector = amend_jis(root[index][1][diff][2].text)
                        diff_table[diff].notes = int(root[index][1][diff][7][0].text)
                        diff_table[diff].peak = int(root[index][1][diff][7][1].text)
                        diff_table[diff].tsumami = int(root[index][1][diff][7][2].text)
                        diff_table[diff].tricky = int(root[index][1][diff][7][3].text)
                        diff_table[diff].handTrip = int(root[index][1][diff][7][4].text)
                        diff_table[diff].oneHand = int(root[index][1][diff][7][5].text)
                    except IndexError:
                        break

                index += 1
            except IndexError:
                break

        timber.debug('Parse data from music_db.xml complete.')

        # clean up the utf-8 xml file
        try:
            os.remove(utf_path)
        except FileNotFoundError:
            pass

    def _parse_aka_db(self):
        jis_path = self._data_dir + '/others/akaname_parts.xml'
        timber.debug(f'Get akaname_parts.xml path [{jis_path}]')
        if not path.exists(jis_path):
            timber.error('Path of ./contents/data/others/akaname_parts.xml is unavailable, '
                         'please check your file directory.'
                         'File paths were given in log file(timber.log).')
            input('Press enter to continue')
            exit(1)

        # convert cp932 to utf-8, again
        # 我感谢日本国全国人民
        jis_xml = open(jis_path, 'r', encoding='cp932')
        jis_data = jis_xml.readlines()
        jis_xml.close()

        utf_path = self._data_dir + '/akaname_parts.xml'
        utf_xml = open(utf_path, 'w', encoding='utf-8')
        utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
        jis_data.pop(0)
        for line in jis_data:
            utf_xml.write(line)
        utf_xml.close()

        # Get database for akaname
        tree = parse(utf_path)
        root = tree.getroot()

        index = 0
        while True:
            try:
                aka_id = int(root[index].attrib['id'])
                aka_name = amend_jis(root[index][0].text)
                self.akaDataMap.append(AkaData(aka_id, aka_name))
                index += 1
            except IndexError:
                break

        self.akaDataMap.pop(0)
        timber.debug('Parse data from akaname_parts.xml complete.')

        # clean up the utf-8 xml file
        try:
            os.remove(utf_path)
        except FileNotFoundError:
            pass

    def _parse_meme_db(self):
        """TODO: THIS"""

    def _write_database(self):
        timber.debug('Building music.sqlite3 database')
        # setup table 'METADATA'
        CREATE_METADATA, INSERT_METADATA = \
            sh.CREATE_AND_INSERT_METADATA(METADATA_VERSION, self._get_metadata_content(METADATA_VERSION))
        self._cur.execute(sh.DROP_METADATA)
        self._cur.execute(CREATE_METADATA)
        self._cur.execute(INSERT_METADATA)
        timber.debug(f'Construct table \'METADATA\' with version {METADATA_VERSION}')

        # setup table 'MUSIC'
        self._cur.execute(sh.DROP_MUSIC)
        self._cur.execute(sh.CREATE_MUSIC)
        for music_data in self.musicDataMap:
            if music_data.mID:
                i_music = sh.INSERT_MUSIC(music_data)
                self._cur.execute(i_music)
        timber.debug(f'Construct table \'MUSIC\' with {self.mapSize} songs')

        # setup table 'AKA'
        self._cur.execute(sh.DROP_AKA)
        for aka_data in self.akaDataMap:
            if aka_data.akaID:
                pass
        timber.debug(f'Construct table \'AKA\' with {len(self.akaDataMap)} records')

        # setup table ''MEME
        self._cur.execute(sh.DROP_MEME)

    def _get_metadata_content(self, meta_ver: int) -> dict:
        if meta_ver == 1:
            return {'SDVX_VER': self._game_version, 'MAP_SIZE': self.mapSize, 'FIX_VER': METADATA_FIX_VERSION}
        else:
            raise RuntimeError('Unsupported metadata version.')

    def _read_metadata_content(self, fetch_res: list) -> bool:
        meta_ver = fetch_res[0]
        if meta_ver < METADATA_VERSION:
            return False
        elif meta_ver > METADATA_VERSION:
            timber.warning('The metadata version of existing database is higher than program\'s somehow. '
                           'The program will try to overwrite it with a lower version, please confirm it to do so.')
            op = input('[Y/N]:').upper()
            if op == 'Y':  # force update(really?)
                return False
            else:
                exit(1)
        if meta_ver == 1:
            meta_ver, fix_ver, game_ver, map_size = fetch_res
            if game_ver < self._game_version:  # outdated game
                return False
            if fix_ver < METADATA_FIX_VERSION:
                return False

        return True  # finally you make it!
