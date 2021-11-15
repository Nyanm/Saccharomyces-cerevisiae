import os
import re
import json
import sys
import time
import pyfiglet
import numpy as np

from cfg_read import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg_read import Timber
from update.update_init import update
from genre.gen6 import main_plot_gen6, tools_plot_gen6
from genre.gen5 import main_plot_gen5

# Dictionary for vf calculation
clear_factor = {1: 0.5, 2: 1.0, 3: 1.02, 4: 1.05, 5: 1.10}
grade_factor = {1: 0.80, 2: 0.82, 3: 0.85, 4: 0.88, 5: 0.91, 6: 0.94, 7: 0.97, 8: 1.00, 9: 1.02, 10: 1.05}

# Look up table for crew, only support crew with LIVE-2D
crew_id = {116: '0001', 95: '0002', 96: '0003', 100: '0004', 101: '0005', 102: '0006', 103: '0007', 104: '0008',
           105: '0009', 106: '0010', 107: '0011', 109: '0012', 112: '0013', 113: '0014', 117: '0015', 118: '0016',
           119: '0017', 120: '0018', 121: '0019'}

timber = Timber('main.py')
skin_dict = {'gen6': main_plot_gen6, 'gen5': main_plot_gen5}

title = pyfiglet.Figlet(width=1000)
title_text = title.renderText('Saccharomyces\n              cerevisiae')
title_text += '                    Simple SDVX@Asphyxia Score Checker                    \n' \
              '                             Version 2.0 beta\n' \
              '                       Powered by Nyanm & Achernar\n\n' \
              '查分器功能  Score checker function field\n' \
              '[1] B50成绩查询   Best 50 Songs query    [2] 玩家点灯总结  User summary        \n' \
              '[3] 最近游玩记录  Recent play record     [4] 特定歌曲记录  Specific song record\n\n' \
              '通常功能    Common function field\n' \
              '[8] 搜索歌曲mid  Search mid              [9] 可用皮肤列表  Available skin list\n' \
              '[0] 退出  Exit\n\n' \
              '输入相应数字后回车以继续  Enter corresponding number to continue:'


class SDVX:

    def __init__(self):

        # Load skin
        try:
            self.plot_skin = skin_dict[skin_name]
        except KeyError:
            timber.error('Invalid skin name, please check your configurations.')

        if is_init is None:
            update()

        # Read sdvx@asphyxia.db
        self.raw_data = open(db_dir, 'r')
        self.music_map = [[False, '', '', '', '', '', '', '', '', '', 0.0] for _ in range(map_size * 5 + 1)]
        """
        music_map is a comprehensive map to store player's play record
        It contains 5-time of map_size lines, each 5 lines define the 5 difficulties of a single song
        Each line of music map should be:
        [is_recorded: bool, mid: int, type: int, score: int, clear: int, grade: int, 
         timestamp: int, name: str, lv: str, inf_ver: str, vf: float]
        """
        timber.info('Load data from sdvx@asphyxia.db')

        # Load level table
        try:
            self.level_table = np.load(local_dir + '/data/level_table.npy')
            self.search_db = np.load(local_dir + '/data/search_db.npy')
            self.aka_db = np.load(local_dir + '/data/aka_db.npy', allow_pickle=True)
        except FileNotFoundError:
            timber.error('Critical npy files not found, please delete the last line of config.txt and restart.')

        # Get raw data from db
        self.last_record = []
        for line in self.raw_data:
            json_dict = json.loads(line)

            try:  # Some lines have no collection name
                line_type = json_dict['collection']
            except KeyError:
                continue

            if json_dict['__refid'] != card_num:  # Specify user
                continue

            if line_type == 'music':

                mid, m_type, score = json_dict['mid'], json_dict['type'], json_dict['score']
                clear, grade = json_dict['clear'], json_dict['grade']
                m_time = json_dict['updatedAt']['$$date']

                lv = self.level_table[int(mid)][int(m_type) * 3 + 7]
                inf_ver, name = self.level_table[int(mid)][6], self.level_table[int(mid)][1]
                if not lv:
                    lv, inf_ver = '0', '0'
                try:
                    vf = int(lv) * (int(score) / 10000000) * clear_factor[clear] * grade_factor[grade] * 2
                except ValueError:
                    vf = 0.0

                music_index = int(mid) * 5 + int(m_type)
                self.last_record = [True, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf]
                self.music_map[music_index] = self.last_record

            elif line_type == 'profile':
                self.user_name, self.ap_card, self.aka_index = \
                    json_dict['name'], json_dict['appeal'], json_dict['akaname']
            elif line_type == 'skill':
                self.skill = json_dict['base']
            elif line_type == 'param':
                if json_dict['type'] == 2 and json_dict['id'] == 1:
                    self.crew_index = json_dict['param'][24]

        # Unpack last record, profile, skill and param data
        timber.info('Draw data from sdvx@asphyxia.db successfully.')
        try:
            self.akaname = 'よろしくお願いします'  # If you have modified your aka name
            for akaname in self.aka_db:
                if akaname[0] == self.aka_index:
                    self.akaname = akaname[1]
                    break
            try:
                self.crew_id = crew_id[self.crew_index]
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

    def search_mid(self, search_str: str) -> tuple:
        result_list = []
        for index in range(1, map_size):
            if re.search(search_str, self.search_db[index], re.I):
                result_list.append(index)

        if not result_list:  # Find nothing
            return '', 0

        search_res = ('%d result(s) found:\n\n|No  |MID   |[Name]  [Artist]\n' % len(result_list))
        for index in range(len(result_list)):
            __mid = result_list[index]
            search_res += '|%-4d|%-4d  |[%s]  [%s]\n' % \
                          (index + 1, __mid, self.level_table[__mid][1], self.level_table[__mid][2])

        return search_res, len(result_list)

    def get_b50(self):
        b50_text = self.plot_skin.plot_b50(self.music_map.copy(), self.profile)
        input('%s\nPress enter to continue.' % b50_text)

    def get_summary(self, base_lv: int):
        summary_text = self.plot_skin.plot_summary(self.music_map, self.profile, base_lv)
        input('%s\nPress enter to continue.' % summary_text)

    def get_single(self, record: list):
        sg_text = self.plot_skin.plot_single(record, self.profile)
        input('%s\nPress enter to continue.' % sg_text)

    def __1_get_b50(self):
        os.system('cls')
        self.get_b50()

    def __2_get_summary(self):
        os.system('cls')
        base_lv = input('This function will generate summaries form lv.base to lv.20. \n'
                        'Please enter the lv.base you want, default as 17:')
        timber.info('Get summary level "%s"' % base_lv)

        if not base_lv:
            self.get_summary(17)
            return

        try:
            base_lv = int(base_lv)
            if base_lv > 20 or base_lv < 1:
                timber.warning('Invalid level number.')
                return
        except ValueError:
            timber.warning('Invalid level number.')
            return

        self.get_summary(base_lv)

    def __3_get_recent(self):
        print('\nRecent play record:')
        self.get_single(self.last_record)

    def __4_get_specific(self):

        def not_found_handler():
            timber.info('Record not found.')
            input('Record not found. Press enter to continue.')

        __record = []
        __msg = '\nNOV->1   ADV->2   EXH->3   INF/GRV/HVN/VVD/MXM->4\n' \
                '输入指令形如[歌曲mid] [难度(可选)]，默认搜索最高难度，例如: 天极圈 -> 927 4 (或者 927)\n' \
                'Enter operators like "[mid] [diff(optional)], Search highest difficulty as default, \n' \
                'for example: Kyokuken -> 927 4 (or 927)"\n'
        sep_arg = input(__msg).split()
        timber.info('Get specific "%s"' % ''.join(sep_arg))

        if len(sep_arg) == 1:  # Default highest difficulty
            try:
                mid = int(sep_arg[0])
                if mid > map_size:
                    not_found_handler()
                    return
            except ValueError:
                timber.warning('Invalid character was found, please try again and enter only number(s).\n'
                               'Press enter to continue.')
                return
            for lv_index in range(4, -1, -1):
                index = mid * 5 + lv_index
                if self.music_map[index][0]:
                    __record = self.music_map[index]
                    break

        elif len(sep_arg) == 2:  # Stipulated difficulty
            try:
                mid, m_type = int(sep_arg[0]), int(sep_arg[1])
                if mid > map_size:
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
                    __record = self.music_map[mxm_index]
                elif self.music_map[inf_index][0]:
                    __record = self.music_map[inf_index]

            elif m_type > 0:  # 1st ~ 3rd difficulty
                index = mid * 5 + m_type - 1
                if self.music_map[index][0]:
                    __record = self.music_map[index]

        else:
            timber.warning('Enter operators no more than 2. Press enter to continue.\n')
            return

        if not __record:
            not_found_handler()
            return

        print('\nPlay record for "%s":' % ''.join(sep_arg))
        self.get_single(__record)

    def __8_search(self):
        os.system('cls')
        __msg = '输入想要查询的歌曲的相关信息(曲名、作者或者梗)后回车，不区分大小写\n' \
                'Enter relative message(Name, Artist, Memes) about the song you want to search, not case-sensitive:'
        search_arg = input(__msg)
        timber.info('Searching "%s"' % __msg)
        if search_arg:
            search_res, res_num = self.search_mid(search_arg)
            if res_num:
                timber.info(search_res)
                print('\n共搜索到%d个结果  %s' % (res_num, search_res))
            else:
                print('\n未能搜索到结果  No search result found')
                timber.info('Search failed.')
        else:
            print('Empty input. Please try again and at least enter something.')
        input('Press enter to continue.')

    def __9_skin_list(self):
        timber.info('Damn I have no spare skins to show.')
        input('\nApparently the only skin we have is the primary skin for Saccharomyces cerevisiae:[gen6] :(\n'
              'But you, %s, you can join us and help us to develop new skins!\n' % self.user_name)

    def __0_see_you_next_time(self):
        timber.info('Exit by op num 0.')
        print('\nSee you next time, %s' % self.user_name)
        time.sleep(1)
        sys.exit(0)

    def input_handler(self):
        key_dict = {
            '1': self.__1_get_b50,
            '2': self.__2_get_summary,
            '3': self.__3_get_recent,
            '4': self.__4_get_specific,
            '8': self.__8_search,
            '9': self.__9_skin_list,
            '0': self.__0_see_you_next_time
        }

        os.system('cls')
        time.sleep(0.05)
        print(title_text, end='')
        while True:
            base_arg = input()
            timber.info('Get user operator %s' % base_arg)
            try:
                key_dict[base_arg]()
                break
            except KeyError:
                pass


if __name__ == '__main__':
    sdvx = SDVX()
    while True:
        sdvx.input_handler()
