import os
import re
import json
import sys
import time
import numpy as np
from xml.etree.cElementTree import parse

from .cfg_read import local_dir, cfg
from .cfg_read import Timber
from utli import draft, sheet
from update.__init__ import update
import genre.gen6.main
import genre.gen5.main

timber = Timber('main.py')
skin_dict = {'gen6': genre.gen6.main, 'gen5': genre.gen5.main}
VERSION = [1, 2, 'alpha']


class SDVX:

    def __init__(self):

        # Load skin
        try:
            self.plot_skin = skin_dict[cfg.skin_name]
        except KeyError:
            timber.error('Invalid skin name, please check your configurations.')

        # Update check
        ea3_path = '/'.join(cfg.game_dir.split('/')[:-1]) + '/prop/ea3-config.xml'
        tree = parse(ea3_path)
        root = tree.getroot()
        cur_ver = int(root[1][4].text)

        if not cfg.is_init:
            update()
            cfg.set_init_sign()
            cfg.set_version(cur_ver)
        elif cur_ver > cfg.version:
            update(game_only=True)
            cfg.set_version(cur_ver)

        # Read sdvx@asphyxia.db
        self.raw_data = open(cfg.db_dir, 'r')
        self.music_map = [[False, 0, 0, 0, 0, 0, 0, 'None', '0', '0', 0.0, 0] for _ in range(cfg.map_size * 5 + 1)]
        """
        music_map is a comprehensive map to store player's play record
        It contains 5-time of map_size lines, each 5 lines define the 5 difficulties of a single song
        Each line of music map should be:
        [
            0:  is_recorded: bool, 
            1:  mid: int, 
            2:  music_type: int, 
            3:  score: int, 
            4:  clear: int, 
            5:  grade: int, 
            6:  timestamp: int, 
            7:  name: str, 
            8:  lv: str, 
            9:  inf_ver: str, 
            10: vf: float, 
            11: exscore: int
        ]
        """
        timber.info('Load data from sdvx@asphyxia.db')

        # Load level table
        try:
            self.level_table = np.load(local_dir + '/data/level_table.npy')
            self.search_db = np.load(local_dir + '/data/search_db.npy')
            self.aka_db = np.load(local_dir + '/data/aka_db.npy', allow_pickle=True)
        except FileNotFoundError:
            timber.error('Critical npy files not found, please delete the last line of config.cfg and restart.')

        # Get raw data from db
        self.last_index, self.skill = 0, 0
        skill_time, profile_time, crew_time = 0, 0, 0
        for line in self.raw_data:
            json_dict = json.loads(line)

            try:  # Some lines have no collection name
                line_type = json_dict['collection']
            except KeyError:
                continue

            try:
                cur_id = json_dict['__refid']
                cur_time = json_dict['updatedAt']['$$date']
            except KeyError:
                continue

            if cur_id != cfg.card_num:  # Specify user
                continue

            if line_type == 'music':

                mid, m_type, score = json_dict['mid'], json_dict['type'], json_dict['score']
                clear, grade = json_dict['clear'], json_dict['grade']
                m_time = cur_time

                try:
                    lv = self.level_table[mid][m_type * 3 + 10]
                except IndexError:
                    lv = 9961
                    timber.error('The value "map size" in config.cfg may be too small, '
                                 'try to set a bigger one and restart the application.')
                    cfg.set_init_sign(False)

                inf_ver, name = self.level_table[mid][9], self.level_table[mid][1]
                if not lv:
                    lv, inf_ver = '0', '0'

                try:
                    vf = int(lv) * (score / 10000000) * sheet.clear_factor[clear] * sheet.grade_factor[grade] * 2
                except ValueError:
                    vf = 0.0
                try:
                    exscore = json_dict['exscore']
                except KeyError:
                    exscore = 0

                self.last_index = mid * 5 + m_type
                self.music_map[self.last_index] = \
                    [True, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf, exscore]

            elif line_type == 'profile':
                if cur_time > profile_time:
                    profile_time = cur_time
                    self.user_name, self.ap_card, self.aka_index = \
                        json_dict['name'], json_dict['appeal'], json_dict['akaname']
            elif line_type == 'skill':
                if cur_time > skill_time:
                    skill_time = cur_time
                    self.skill = max(json_dict['base'], self.skill)
            elif line_type == 'param':
                if json_dict['type'] == 2 and json_dict['id'] == 1:
                    if cur_time > crew_time:
                        crew_time = cur_time
                        self.crew_index = json_dict['param'][24]

        if not self.last_index:
            timber.error('Music record not found, make sure you have at least played once (and saved successfully).')

        # Unpack last record, profile, skill and param data
        timber.info('Draw data from sdvx@asphyxia.db successfully.')
        try:
            self.akaname = 'よろしくお願いします'  # If you have modified your aka name
            for akaname in self.aka_db:
                if int(akaname[0]) == self.aka_index:
                    self.akaname = akaname[1]
                    break
            try:
                self.crew_id = sheet.crew_id[self.crew_index]
            except KeyError:
                self.crew_id = '0014'  # Gen 6 Rasis

            timber.info('Profile data load successfully.\n\n'
                        'user name   :%s\nappeal card :%d\nakaname     :%s\nskill       :%d\ncrew        :%s\n' %
                        (self.user_name, self.ap_card, self.akaname, self.skill, self.crew_id))
        except AttributeError:
            timber.error('Profile/Skill/Crew data not found, '
                         'make sure you have at least played once (and saved successfully).')

        self.profile = [self.user_name, self.ap_card, self.akaname, self.skill, self.crew_id]
        timber.info('Initialization complete.')

    def __get_b50(self):
        b50_text = self.plot_skin.plot_b50(self.music_map.copy(), self.profile)
        input('%s\nPress enter to continue.' % b50_text)

    def __get_summary(self, base_lv: int):
        summary_text = self.plot_skin.plot_summary(self.music_map.copy(), self.profile, base_lv)
        input('%s\nPress enter to continue.' % summary_text)

    def __get_single(self, sg_index: int):
        sg_text = self.plot_skin.plot_single(self.music_map.copy(), self.profile, sg_index)
        input('%s\nPress enter to continue.' % sg_text)

    def __get_level(self, level: int, limits: tuple, grade_flag: str):
        level_text = self.plot_skin.plot_level(self.music_map, self.profile, level, limits, grade_flag)
        input('%s\nPress enter to continue.' % level_text)

    def _1_get_b50(self):
        os.system('cls')
        self.__get_b50()

    def _2_get_summary(self):
        os.system('cls')
        base_lv = input(draft.TwoGetSummary.init_hint())
        timber.info('Get summary from level "%s"' % base_lv)

        if not base_lv:
            self.__get_summary(17)
            return

        try:
            base_lv = int(base_lv)
            if base_lv > 20 or base_lv < 1:
                timber.warning('Invalid level number.')
                return
        except ValueError:
            timber.warning('Invalid level number.')
            return

        self.__get_summary(base_lv)

    def _3_get_recent(self):
        print(draft.ThreeGetRecent.init_hint())
        __music_map = self.music_map.copy()
        __music_map.sort(key=lambda x: x[6])
        latest = __music_map[-1]
        self.__get_single(latest[1] * 5 + latest[2])

    def _4_get_specific(self):

        def not_found_handler():
            timber.info('Record not found.')
            input(draft.FourGetSpecific.not_found())

        sg_index = 0
        sep_arg = input(draft.FourGetSpecific.init_hint()).split()
        timber.info('Get specific "%s"' % ' '.join(sep_arg))

        if len(sep_arg) == 1:  # Default highest difficulty
            try:
                mid = int(sep_arg[0])
                if mid > cfg.map_size:
                    not_found_handler()
                    return
            except ValueError:
                timber.warning('Invalid character was found, please try again and enter only number(s).\n'
                               'Press enter to continue.')
                return
            for lv_index in range(4, -1, -1):
                index = mid * 5 + lv_index
                if self.music_map[index][0]:
                    sg_index = index
                    break

        elif len(sep_arg) == 2:  # Stipulated difficulty
            try:
                mid, m_type = int(sep_arg[0]), int(sep_arg[1])
                if mid > cfg.map_size:
                    not_found_handler()
                    return
            except ValueError:
                timber.warning('Invalid character was found, please try again and enter only number(s).\n'
                               'Press enter to continue.')
                return
            if m_type >= 4:  # 4th difficulty
                mxm_index = mid * 5 + m_type
                inf_index = mid * 5 + m_type - 1
                if self.music_map[mxm_index][0]:
                    sg_index = mxm_index
                elif self.music_map[inf_index][0]:
                    sg_index = inf_index

            elif m_type > 0:  # 1st ~ 3rd difficulty
                index = mid * 5 + m_type - 1
                if self.music_map[index][0]:
                    sg_index = index

        else:
            timber.warning('Enter operators no more than 2. Press enter to continue.\n')
            return

        if not sg_index:
            not_found_handler()
            return

        print(draft.FourGetSpecific.search_res(sep_arg))
        self.__get_single(sg_index)

    def _5_get_level(self):
        os.system('cls')
        level = input(draft.FiveGetLevel.init_hint())
        timber.info('Level "%s"' % level)
        try:
            level = int(level)
            if level > 20 or level < 1:
                timber.warning('Invalid level number. Please enter a positive number no more than 20.')
                return
        except ValueError:
            timber.warning('Invalid input. Please enter a positive number no more than 20.')
            return

        threshold = input(draft.FiveGetLevel.threshold()).upper().replace('P', '+')
        timber.info('Score limit %s' % threshold)

        if not threshold:  # entered nothing, default as querying all
            limits, grade_flag = (0, 10000000), 'ALL'
            print(draft.FiveGetLevel.all_songs(level))
        else:  # entered something, need further validity check
            try:
                # scores at a specific grade
                limits = sheet.score_table[threshold]
                grade_flag = threshold
            except KeyError:
                # scores between 2 limits

                # thou should enter only 2 numbers separated with '-'
                limits = threshold.split('-')
                if len(limits) != 2:
                    timber.warning('Invalid score. Please enter two positive numbers separated with "-".')
                    return

                try:  # thou should enter numbers between 0 and 10m
                    lim_1, lim_2 = int(limits[0]), int(limits[1])
                    if lim_1 > 10000000 or lim_1 < 0 or lim_2 > 10000000 or lim_2 < 0:
                        raise ValueError('')
                except ValueError:
                    timber.warning('Invalid input. Please enter two positive numbers no more than 10000000.')
                    return

                limits, grade_flag = (min(lim_1, lim_2), max(lim_1, lim_2)), None

            if grade_flag:
                print(draft.FiveGetLevel.grade_songs(level, grade_flag))
            else:
                print(draft.FiveGetLevel.limit_songs(level, limits[0], limits[1]))
        self.__get_level(level, limits, grade_flag)

    def _8_search(self):
        os.system('cls')
        search_str = input(draft.EightSearch.init_hint())
        timber.info('Searching "%s"' % search_str)
        if search_str:

            result_list = []
            for index in range(1, cfg.map_size):
                try:
                    if re.search(search_str, self.search_db[index], re.I):
                        result_list.append(index)
                except re.error:
                    timber.info_clog('Invalid character (for regular expression) was entered, '
                                     'which crashed this query. Press enter to continue.')
                    return

            search_res = ('%d result(s) found:\n\n'
                          '|No  |MID   |Level        |Date        |Yomigana\n'
                          '     |Name  -  Artist\n\n' % len(result_list))
            for index in range(len(result_list)):
                __mid = result_list[index]
                __data = self.level_table[__mid]
                __date = '%s/%s/%s' % (__data[7][:4], __data[7][4:6], __data[7][6:])
                search_res += '|%-4d|%-4d  |%s/%s/%s/%s  |%-8s  |%s\n     |%s  -  %s\n\n' % \
                              (index + 1, __mid, __data[10].zfill(2), __data[13].zfill(2), __data[16].zfill(2),
                               str(int(__data[19]) + int(__data[22])).zfill(2), __date, __data[2], __data[1], __data[3])

            res_num = len(result_list)

            if res_num:
                timber.info(search_res)
                print(draft.EightSearch.success(res_num, search_res))
            else:
                print(draft.EightSearch.failed())
                timber.info('Search failed.')
        else:
            print(draft.EightSearch.empty())
        input(draft.CommonMsg.enter())

    def _9_faq(self):
        os.system('cls')
        timber.info('FAQ')
        print(draft.NineFAQ.first(self.user_name))
        print(draft.NineFAQ.second())

        input(draft.CommonMsg.enter())

    def _0_see_you_next_time(self):
        timber.info('Exit by operator number 0.')
        print(draft.ZeroExit.farewell(self.user_name))
        time.sleep(1.5)
        sys.exit(0)

    @staticmethod
    def _10_donate():
        os.system('cls')
        timber.info('Ali-pay is also recommended.')
        print(draft.TenDonate.init_hint())

        input(draft.TenDonate.back_to_light())

    def input_handler(self):
        key_dict = {
            '1': self._1_get_b50,
            '2': self._2_get_summary,
            '3': self._3_get_recent,
            '4': self._4_get_specific,
            '5': self._5_get_level,
            '8': self._8_search,
            '9': self._9_faq,
            '0': self._0_see_you_next_time,
            '10': self._10_donate
        }

        os.system('cls')
        time.sleep(0.05)
        print(draft.TitleMsg.title(VERSION), end='')
        while True:
            base_arg = input()
            timber.info('Get user operator %s' % base_arg)
            try:
                key_dict[base_arg]()
                break
            except KeyError:
                pass
