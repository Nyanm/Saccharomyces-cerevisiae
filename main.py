import os
import re
import json
import sys
import time
import numpy as np
import qrcode
import base64
from traceback import format_exc
from xml.etree.cElementTree import parse

from cfg_read import local_dir, cfg
from cfg_read import Timber
from update.update_init import update
from genre.gen6 import main_plot_gen6
from genre.gen5 import main_plot_gen5

# Dictionary for vf calculation
clear_factor = {0: 0, 1: 0.5, 2: 1.0, 3: 1.02, 4: 1.05, 5: 1.10}
grade_factor = {0: 0, 1: 0.80, 2: 0.82, 3: 0.85, 4: 0.88, 5: 0.91, 6: 0.94, 7: 0.97, 8: 1.00, 9: 1.02, 10: 1.05}

# Look up table for crew, only support crew with LIVE-2D
crew_id = {116: '0001', 95: '0002', 96: '0003', 100: '0004', 101: '0005', 102: '0006', 103: '0007', 104: '0008',
           105: '0009', 106: '0010', 107: '0011', 109: '0012', 112: '0013', 113: '0014', 117: '0015', 118: '0016',
           119: '0017', 120: '0018', 121: '0019'}

timber = Timber('main.py')
skin_dict = {'gen6': main_plot_gen6, 'gen5': main_plot_gen5}

# pyfiglet conflict with pyinstaller
title_text = " ____                 _                                                   \n" \
             "/ ___|  __ _  ___ ___| |__   __ _ _ __ ___  _ __ ___  _   _  ___ ___  ___ \n" \
             "\___ \ / _` |/ __/ __| '_ \ / _` | '__/ _ \| '_ ` _ \| | | |/ __/ _ \/ __|\n" \
             " ___) | (_| | (_| (__| | | | (_| | | | (_) | | | | | | |_| | (_|  __/\__ \\\n" \
             "|____/ \__,_|\___\___|_| |_|\__,_|_|  \___/|_| |_| |_|\__, |\___\___||___/\n" \
             "                                                      |___/               \n" \
             "                                       _     _            \n" \
             "                ___ ___ _ __ _____   _(_)___(_) __ _  ___ \n" \
             "               / __/ _ \ '__/ _ \ \ / / / __| |/ _` |/ _ \\\n" \
             "              | (_|  __/ | |  __/\ V /| \__ \ | (_| |  __/\n" \
             "               \___\___|_|  \___| \_/ |_|___/_|\__,_|\___|\n" \
             "\n" \
             "                    Simple SDVX@Asphyxia Score Checker                    \n" \
             "                              Version 1.1.2\n" \
             "                       Powered by Nyanm & Achernar\n\n" \
             "查分器功能  Score checker function field\n" \
             "[1] B50成绩查询   Best 50 Songs query    [2] 玩家点灯总结  User summary        \n" \
             "[3] 最近游玩记录  Recent play record     [4] 特定歌曲记录  Specific song record\n" \
             "[5] 歌曲分数列表  Score list\n\n" \
             "通常功能    Common function field\n" \
             "[8] 搜索歌曲mid  Search mid              [9] 常见问题  FAQ\n" \
             "[0] 退出  Exit\n\n" \
             "输入相应数字后回车以继续  Enter corresponding number to continue:"


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
        for line in self.raw_data:
            json_dict = json.loads(line)

            try:  # Some lines have no collection name
                line_type = json_dict['collection']
            except KeyError:
                continue

            try:
                cur_id = json_dict['__refid']
            except KeyError:
                continue

            if json_dict['__refid'] != cur_id:  # Specify user
                continue

            if line_type == 'music':

                mid, m_type, score = json_dict['mid'], json_dict['type'], json_dict['score']
                clear, grade = json_dict['clear'], json_dict['grade']
                m_time = json_dict['updatedAt']['$$date']

                try:
                    lv = self.level_table[mid][m_type * 3 + 7]
                except IndexError:
                    lv = 9961
                    timber.error('The value "map size" in config.cfg may be too small, '
                                 'try to set a bigger one and restart the application.')
                    cfg.set_init_sign(False)

                inf_ver, name = self.level_table[mid][6], self.level_table[mid][1]
                if not lv:
                    lv, inf_ver = '0', '0'

                try:
                    vf = int(lv) * (score / 10000000) * clear_factor[clear] * grade_factor[grade] * 2
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
                self.user_name, self.ap_card, self.aka_index = \
                    json_dict['name'], json_dict['appeal'], json_dict['akaname']
            elif line_type == 'skill':
                self.skill = max(json_dict['base'], self.skill)
            elif line_type == 'param':
                if json_dict['type'] == 2 and json_dict['id'] == 1:
                    self.crew_index = json_dict['param'][24]

        if not self.last_index:
            timber.error('Music record not found, make sure you have at least played once (and saved successfully).')

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

    def __get_b50(self):
        b50_text = self.plot_skin.plot_b50(self.music_map.copy(), self.profile)
        input('%s\nPress enter to continue.' % b50_text)

    def __get_summary(self, base_lv: int):
        summary_text = self.plot_skin.plot_summary(self.music_map.copy(), self.profile, base_lv)
        input('%s\nPress enter to continue.' % summary_text)

    def __get_single(self, sg_index: int):
        sg_text = self.plot_skin.plot_single(self.music_map.copy(), self.profile, sg_index)
        input('%s\nPress enter to continue.' % sg_text)

    def __get_level(self, level: int, threshold: int):
        level_text = self.plot_skin.plot_level(self.music_map, self.profile, level, threshold)
        input('%s\nPress enter to continue.' % level_text)

    def _1_get_b50(self):
        os.system('cls')
        self.__get_b50()

    def _2_get_summary(self):
        os.system('cls')
        base_lv = input('This function will generate summaries form lv.base to lv.20. \n'
                        'Please enter the lv.base you want, default as 17:')
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
        print('\nRecent play record:')
        __music_map = self.music_map.copy()
        __music_map.sort(key=lambda x: x[6])
        latest = __music_map[-1]
        self.__get_single(latest[1] * 5 + latest[2])

    def _4_get_specific(self):

        def not_found_handler():
            timber.info('Record not found.')
            input('Record not found. Press enter to continue.')

        sg_index = 0
        __msg = '\nNOV->1   ADV->2   EXH->3   INF/GRV/HVN/VVD/MXM->4\n' \
                '输入指令形如[歌曲mid] [难度(可选)]，默认搜索最高难度，例如: 天极圈 -> 927 4 (或者 927)\n' \
                'Enter operators like "[mid] [diff(optional)], Search highest difficulty as default, \n' \
                'for example: Kyokuken -> 927 4 (or 927)"\n'
        sep_arg = input(__msg).split()
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

        print('\nPlay record for "%s":' % ''.join(sep_arg))
        self.__get_single(sg_index)

    def _5_get_level(self):
        os.system('cls')
        level = input('输入需要查询的歌曲等级\n'
                      'Enter the level you want to query (1~20):')
        timber.info('Level "%s"' % level)
        try:
            level = int(level)
            if level > 20 or level < 1:
                timber.warning('Invalid level number. Please enter a positive number no more than 20.')
                return
        except ValueError:
            timber.warning('Invalid input. Please enter a positive number no more than 20.')
            return

        threshold = input('输入所查的最低分数，默认查询全部\n'
                          'Enter the bottom score you want to query, default as 0:')
        if not threshold:
            threshold = 0
        try:
            threshold = int(threshold)
            if threshold > 10000000 or threshold < 0:
                timber.warning('Invalid score. Please enter a positive number no more than 10000000.')
                return
        except ValueError:
            timber.warning('Invalid input. Please enter a positive number no more than 10000000.')
            return

        print('Score list for level %d above %d score:\n' % (level, threshold))
        self.__get_level(level, threshold)

    def _8_search(self):
        os.system('cls')
        __msg = '输入想要查询的歌曲的相关信息(曲名、作者或者梗)后回车，不区分大小写\n' \
                'Enter relative message(Name, Artist, Memes) about the song you want to search, not case-sensitive:'
        search_str = input(__msg)
        timber.info('Searching "%s"' % search_str)
        if search_str:

            result_list = []
            for index in range(1, cfg.map_size):
                if re.search(search_str, self.search_db[index], re.I):
                    result_list.append(index)

            search_res = ('%d result(s) found:\n\n|No  |MID   |[Name]  [Artist]\n' % len(result_list))
            for index in range(len(result_list)):
                __mid = result_list[index]
                search_res += '|%-4d|%-4d  |[%s]  [%s]\n' % \
                              (index + 1, __mid, self.level_table[__mid][1], self.level_table[__mid][2])
            res_num = len(result_list)

            if res_num:
                timber.info(search_res)
                print('\n共搜索到%d个结果  %s' % (res_num, search_res))
            else:
                print('\n未能搜索到结果  No search result found')
                timber.info('Search failed.')
        else:
            print('Empty input. Please try again and at least enter something.')
        input('Press enter to continue.')

    def _9_faq(self):
        os.system('cls')
        timber.info('FAQ')
        print('[1] 为什么新歌不显示？  Why some of the newest songs don\'t appear?\n'
              'zh. 将config.cfg中的"is initialized"项置为"False"或"0"，重启软件，软件将强制对数据库进行更新。\n'
              'en. Try to set the "is initialized" in config.cfg to "False" or "0" and restart the application. '
              'This will force the application to update the databases.\n')
        print('[2] 还有其他皮肤吗？  Is there any other skin?\n'
              'zh. 显然这软件只有gen6一个默认皮肤:(\n'
              '    但是%s，你可以加入我们来开发新的皮肤！\n'
              'en. Apparently the only skin we have is the primary skin for Saccharomyces cerevisiae:[gen6] :(\n'
              '    But you, %s, you can join us and help us to develop new skins!\n' % (self.user_name, self.user_name))
        print('[3] 源码在哪里看？  Where can I get the source code?\n'
              ' -  https://github.com/Nyanm/Saccharomyces-cerevisiae, and welcome to star my project!\n'
              '    Also, the up-to-date release will be uploaded to here.\n')
        print('[4] 为什么软件里有这么多工地英语？\n'
              ' -  说来惭愧，这软件最开始甚至只有英文，中文是我后来加的（\n')

        input('Press enter to continue.')

    def _0_see_you_next_time(self):
        timber.info('Exit by operator number 0.')
        print('\nSee you next time, %s' % self.user_name)
        time.sleep(2)
        sys.exit(0)

    @staticmethod
    def _10_donate():
        os.system('cls')
        timber.info('Ali-pay is also recommended.')
        print('恭喜你发现了月之暗面！这里是一个赞助页面，可以请开发者喝一杯咖啡~\n'
              'Congratulations! You\'ve found the dark side of the moon!\n'
              'Here is a donate page, where you can buy the developer a cup of coffee if you like this application.\n'
              '↓↓↓ 微信二维码    Wechat QrCode ↓↓↓\n')

        __msg = ''
        qr = qrcode.QRCode()
        qr.add_data(
            base64.b64decode('aHR0cHM6Ly92ZHNlLmJkc3RhdGljLmNvbS8vMTkyZDlhOThkNzgyZDljNzRjOTZmMDlkYjkzNzhkOTMubXA0')
        )
        __mat = qr.get_matrix()

        for line in __mat:
            for column in line:
                if column:
                    __msg += '  '
                else:
                    __msg += '██'
            __msg += '\n'

        print(__msg)
        input('Press enter to return light side.')

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
    try:
        sdvx = SDVX()
        while True:
            sdvx.input_handler()
    except Exception:
        timber.error('Fatal error occurs, please report the following message to developer.\n\n%s\n'
                     % format_exc())

# pyinstaller -i sjf.ico -F main.py
