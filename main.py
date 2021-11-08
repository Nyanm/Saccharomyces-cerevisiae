import time

from cfg_read import *
from os import path
from xml.etree.cElementTree import parse
from numpy import array, save, load, zeros
from csv import reader
from copy import deepcopy
from traceback import format_exc

import plot_gen6
import plot_gen5

file_name = 'main.py'

clear_factor = {'1': 0.5, '2': 1.0, '3': 1.02, '4': 1.05, '5': 1.10}
clear_index = {2: 0, 3: 1, 4: 2, 5: 3}

grade_factor = {'1': 0.80, '2': 0.82, '3': 0.85, '4': 0.88, '5': 0.91,
                '6': 0.94, '7': 0.97, '8': 1.00, '9': 1.02, '10': 1.05}
grade_index = {8: 4, 9: 5, 10: 6}

get_card = re.compile(r'"__refid":"+[^"]*')
get_name = re.compile(r'"name":"+[^"]*')
get_aka = re.compile(r'"akaname":+[^,]*')
get_ap_card = re.compile(r'"appeal":+[^,]*')
get_base = re.compile(r'"base":+[^,]*')

get_mid = re.compile(r'"mid":+[^,]*')
get_type = re.compile(r'"type":+[^,]*')
get_score = re.compile(r'"score":+[^,]*')
get_clear = re.compile(r'"clear":+[^,]*')
get_grade = re.compile(r'"grade":+[^,]*')
get_time = re.compile(r'"updatedAt":+[^,]*')

menu_msg = '\n查分器功能  Score checker function field\n' \
           '1----B50成绩查询及VF分析  Best 50 Songs and VF analysis\n' \
           '2----最近游玩记录  Recent play record\n' \
           '3----特定歌曲记录  Specific song record\n' \
           '4----玩家点灯总结  User summary\n' \
           '普适功能  Universal function field\n' \
           '8----搜索歌曲mid  Search mid\n' \
           '9----显示可用皮肤列表  Show available skin list\n' \
           '0----退出  Exit\n' \
           '输入相应数字后回车以继续  Enter corresponding number to continue:'
specific_msg = 'NOV->1, ADV->2, EXH->3, INF/GRV/HVN/VVD/MXM->4\n' \
               '默认搜索最高难度  Search highest difficulty as default\n' \
               '输入指令形如[歌曲mid] [难度(可选)]  Enter operators like \'[mid] [diff(optional)]\':'
search_msg = '输入想要查询的歌曲的相关信息(曲名、作者或者梗)后回车，不区分大小写\n' \
             'Enter relative message(Name, Artist, Memes) about the song you want to search, not case-sensitive:'
skin_msg = '[01]gen6: primary skin for Saccharomyces cerevisiae'


def error_handler(msg: str):
    log_write(msg, file_name)
    input(msg)
    sys.exit(0)


def get_skin_type(skin_name: str):
    if skin_name == 'gen6':
        return plot_gen6
    if skin_name == 'gen5':
        return plot_gen5
    else:
        error_handler('Invalid skin name, please recheck your configurations.')


class SdvxData:

    def __init__(self):

        # Read config.txt
        self.map_size, self.card_num, self.local_dir, self.db_dir, \
        self.game_dir, self.output, self.skin_name, self.is_init = get_cfg()
        self.plot_skin = get_skin_type(self.skin_name)
        self.data_dir = self.local_dir + '/data'

        # Validity check
        if not path.exists(self.db_dir):
            error_handler(r'sdvx@asphyxia.db not found, please check your file directory.')
        if not path.exists(self.game_dir):
            error_handler(r'KFC-**********\contents\data not found, please check your file directory.')
        if not path.exists(self.output):
            error_handler(r'Output folder not found, please check your file directory.')

        log_write('Set up complete.', file_name)
        log_write('map size=%s' % self.map_size, file_name)
        log_write('card num=%s' % self.card_num, file_name)
        log_write('local dir=%s' % self.local_dir, file_name)
        log_write('db dir=%s' % self.db_dir, file_name)
        log_write('game dir=%s' % self.game_dir, file_name)
        log_write('output=%s' % self.output, file_name)
        log_write('skin name=%s' % self.skin_name, file_name)

        # Initialize check
        if not self.is_init:
            print('Initializing.')
            log_write('No initialized sign, start to initialize level_table.npy and aka_db.npy', file_name)

            # Set up music_db encoded with UTF-8
            jis_xml = open(self.game_dir + r'/others/music_db.xml', 'r', encoding='cp932').readlines()
            utf_xml = open(self.data_dir + r'/music_db_utf8.xml', 'w', encoding='utf-8')
            utf_xml.write('<?xml version="1.0" encoding="utf-8"?>\n')
            jis_xml.pop(0)
            for line in jis_xml:
                utf_xml.write(line)
            utf_xml.close()

            # Get level information from xml, then saved as npy file
            tree = parse(self.data_dir + r'/music_db_utf8.xml')
            root = tree.getroot()
            music_map = [[''] * 22 for _ in range(self.map_size)]
            aka_map = [[''] * 3 for _ in range(self.map_size)]
            for index in range(self.map_size):
                try:
                    # Fill up each line of level_table.npy
                    mid = int(root[index].attrib['id'])
                    name = root[index][0][1].text \
                        .replace("驫", "ā").replace("骭", "ü").replace("驩", "Ø").replace("罇", "ê").replace("曩", "è") \
                        .replace("齷", "é").replace("騫", "á").replace("曦", "à").replace("龕", "€").replace("趁", "Ǣ") \
                        .replace("蹇", "₂").replace("彜", "ū").replace("雋", "Ǜ").replace("隍", "Ü").replace("鬻", "♃") \
                        .replace("鬥", "Ã").replace("鬆", "Ý").replace("齶", "♡").replace("齲", "❤").replace("躔", "★")\
                        .replace('釁', '🍄').replace('頽', 'ä').replace('黻', '*')
                    artist = root[index][0][3].text
                    bpm_max = int(root[index][0][6].text)
                    bpm_min = int(root[index][0][7].text)
                    version = int(root[index][0][13].text)
                    inf_ver = int(root[index][0][15].text)

                    nov_lv = int(root[index][1][0][0].text)
                    nov_ill = root[index][1][0][1].text
                    nov_eff = root[index][1][0][2].text
                    adv_lv = int(root[index][1][1][0].text)
                    adv_ill = root[index][1][1][1].text
                    adv_eff = root[index][1][1][2].text
                    exh_lv = int(root[index][1][2][0].text)
                    exh_ill = root[index][1][2][1].text
                    exh_eff = root[index][1][2][2].text
                    inf_lv = int(root[index][1][3][0].text)
                    inf_ill = root[index][1][3][1].text
                    inf_eff = root[index][1][3][2].text
                    try:
                        mxm_lv = int(root[index][1][4][0].text)
                        mxm_ill = root[index][1][4][1].text
                        mxm_eff = root[index][1][4][2].text
                    except IndexError:
                        mxm_lv = 0
                        mxm_ill = 'dummy'
                        mxm_eff = 'dummy'
                    music_map[int(mid)] = [mid, name, artist, bpm_max, bpm_min, version, inf_ver, nov_lv, nov_ill,
                                           nov_eff, adv_lv, adv_ill, adv_eff, exh_lv, exh_ill, exh_eff, inf_lv,
                                           inf_ill, inf_eff, mxm_lv, mxm_ill, mxm_eff]

                    # Fill up each line of aka_db.npy
                    music_ascii = root[index][0][5].text.replace('_', ' ')
                    aka_map[int(mid)] = [name, artist, music_ascii]

                except IndexError:
                    break

            log_write('music_db_utf8.xml set up complete', file_name)

            try:
                aka_csv = reader(open(self.data_dir + '/raw_aka_db.csv', encoding='utf-8'))
                aka_list = []
                for csv_record in aka_csv:
                    aka_list.append(csv_record)
                for index in range(1, len(aka_list)):
                    if aka_list[index][0] and aka_map[index][0]:
                        aka_map[index] = aka_list[index]
            except FileNotFoundError:
                input('[Warning]raw_aka_db.csv not found, '
                      'this will not stop the program, but will affect the search results.')
                log_write('[Warning]raw_aka_db.csv not found, '
                          'this will not stop the program, but will affect the search results.', file_name)

            log_write('aka_map set up complete', file_name)

            for index in range(self.map_size):
                if aka_map[index][0]:
                    aka_map[index] = ' '.join(aka_map[index])
                else:
                    aka_map[index] = ''

            music_map = array(music_map)
            save(self.data_dir + '/level_table.npy', music_map)
            aka_map = array(aka_map)
            save(self.data_dir + '/aka_db.npy', aka_map)

            # Add flag to config.txt
            raw_file = open(self.local_dir + '/config.txt', 'a')
            raw_file.write('is initialized=True\n')
            raw_file.close()

            print('Initialization complete.')
            log_write('Initialization complete', file_name)

        # Read sdvx@asphyxia.db
        self.raw_data = open(self.db_dir, 'r')
        self.raw_music = []
        self.raw_profile = ''
        self.raw_skill = ''

        log_write('Raw data read complete', file_name)

        # Get raw data from db
        for line in self.raw_data:
            if re.search(r'"collection":"music"', line):
                raw_card = get_card.search(line).group()[11:]
                if raw_card == self.card_num:
                    self.raw_music.append(line)
            elif re.search(r'"collection":"profile"', line):
                raw_card = get_card.search(line).group()[11:]
                if raw_card == self.card_num:
                    self.raw_profile = line
            elif re.search(r'"collection":"skill"', line):
                raw_card = get_card.search(line).group()[11:]
                if raw_card == self.card_num:
                    self.raw_skill = line

        if not self.raw_profile:
            input('Card not found, please recheck your card number, or ensuring that you have saved yet.')
            sys.exit(1)
        if not self.raw_music:
            input('Music record not found, please recheck your card number, '
                  'or ensuring that you have played at least once.')
            sys.exit(1)

        # Specify profile data
        self.user_name = get_name.search(self.raw_profile).group()[8:]
        self.aka = get_aka.search(self.raw_profile).group()[10:]
        self.ap_card = get_ap_card.search(self.raw_profile).group()[9:]
        self.skill = get_base.search(self.raw_skill).group()[7:]

        log_write('Profile read from sdvx@asphyxia.db', file_name)
        log_write('user name=%s' % self.user_name, file_name)
        log_write('ap card=%s' % self.ap_card, file_name)
        log_write('skill=%s' % self.skill, file_name)

        # Specify music data
        self.raw_music.reverse()
        self.level_table = load(self.data_dir + '/level_table.npy')
        self.music_map = [[False, '', '', '', '', '', '', '', '', '', 0.0] for _ in range(self.map_size * 5 + 1)]
        # Each line of music map should be
        # [is_recorded, mid, type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
        for record in self.raw_music:
            mid, m_type, score, clear, grade, m_time, name, lv, inf_ver = self.__get_music_attr(record)
            music_index = int(mid) * 5 + int(m_type)
            if not self.music_map[music_index][0]:
                vf = self.__vf_calculator(mid, m_type, score, clear, grade)
                self.music_map[music_index] = [True, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf]

    def __vf_calculator(self, mid: str, m_type: str, score: str, clear: str, grade: str) -> float:
        lv = self.level_table[int(mid)][int(m_type) * 3 + 7]
        try:
            vf = int(lv) * (int(score) / 10000000) * clear_factor[clear] * grade_factor[grade] * 2
        except ValueError:
            return 0.0
        return vf

    def __get_music_attr(self, record: str):
        mid = get_mid.search(record).group()[6:]
        m_type = get_type.search(record).group()[7:]
        score = get_score.search(record).group()[8:]
        clear = get_clear.search(record).group()[8:]
        grade = get_grade.search(record).group()[8:]
        m_time = get_time.search(record).group()[22:35]

        lv = self.level_table[int(mid)][int(m_type) * 3 + 7]
        inf_ver, name = self.level_table[int(mid)][6], self.level_table[int(mid)][1]
        if not lv:
            lv, inf_ver = '0', '0'

        return mid, m_type, score, clear, grade, m_time, name, lv, inf_ver

    def get_b50(self):
        log_write('start to generate best 50 record for %s' % self.user_name, file_name)
        self.plot_skin.plot_b50(deepcopy(self.music_map),
                                [self.card_num, self.user_name, self.aka, self.ap_card, self.skill])

    def get_recent(self):
        log_write('start to generate recent record for %s' % self.user_name, file_name)
        recent = self.raw_music[0]
        mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver = self.__get_music_attr(recent)
        vf = self.__vf_calculator(mid, m_type, score, clear, grade)
        self.plot_skin.plot_single([mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf],
                                   [self.user_name, self.aka, self.ap_card, self.skill])

    def get_specific(self, arg_mid: int, arg_type: int = 5):
        # Get specific chart
        # 2 will be returned if there is no corresponding record

        if arg_type == 5:
            index = 0
            for m_index in range(4, -1, -1):
                index = arg_mid * 5 + m_index
                if self.music_map[index][0]:
                    break
                index = 0
            if not index:
                return 1
        elif arg_type == 4:
            mxm_index = arg_mid * 5 + arg_type
            inf_index = arg_mid * 5 + arg_type - 1
            if not self.music_map[mxm_index][0] and self.music_map[inf_index][0]:
                index = inf_index
            elif self.music_map[mxm_index][0] and not self.music_map[inf_index][0]:
                index = mxm_index
            else:
                return 2
        else:
            index = arg_mid * 5 + arg_type - 1
            if not self.music_map[index][0]:
                return 2

        log_write('start to generate record [%d] [%d] for %s' % (arg_mid, arg_type, self.user_name), file_name)
        is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf = self.music_map[index]
        self.plot_skin.plot_single([mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf],
                                   [self.user_name, self.aka, self.ap_card, self.skill])
        return 0

    def get_summary(self, base_lv: int = 17):
        if type(base_lv) != int:
            base_lv = 17
        if base_lv > 20 or base_lv < 1:
            base_lv = 17
        log_write('start to generate user summary in new version for %s' % self.user_name, file_name)
        self.plot_skin.plot_summary(deepcopy(self.music_map),
                                    [self.card_num, self.user_name, self.aka, self.ap_card, self.skill], base_lv)

    def search_mid(self, name_str):
        aka_db = load(self.data_dir + '/aka_db.npy')
        result_list = []
        for index in range(self.map_size):
            if re.search(name_str, aka_db[index], re.I):
                result_list.append(index)
        if not result_list:
            print('未能搜索到结果  No search result found')
            log_write('No search result found', file_name)
            return
        print('共搜索到%d个结果  %d result(s) found:' % (len(result_list), len(result_list)))
        log_write('%d result(s) found' % len(result_list), file_name)
        search_result = 'MID   Name//Artist\n'
        for index in result_list:
            search_result += '%-4d  %s\n      %s\n' % (index, self.level_table[index][1], self.level_table[index][2])
        print(search_result)


if __name__ == '__main__':
    if test_mode:
        base = SdvxData()
        print('*' == '*')
        sys.exit(0)

    try:
        base = SdvxData()

        while True:
            op_num = input(menu_msg)
            log_write('User operate number:%s' % op_num, file_name)
            print()

            if op_num == '1':
                base.get_b50()
            elif op_num == '2':
                base.get_recent()
            elif op_num == '3':
                op_spe = input(specific_msg).split()
                log_write('User input:%s' % op_spe, file_name)
                if len(op_spe) == 1:
                    spe_return = base.get_specific(int(op_spe[0]))
                    if spe_return == 1:
                        print('Invalid operator.')
                    elif spe_return == 2:
                        print('Record not found.')
                elif len(op_spe) == 2:
                    spe_return = base.get_specific(int(op_spe[0]), int(op_spe[1]))
                    if spe_return == 1:
                        print('Invalid operator.')
                    elif spe_return == 2:
                        print('Record not found.')
                else:
                    print('Invalid operator.')
            elif op_num == '4':
                base.get_summary()

            elif op_num == '8':
                op_search = input(search_msg)
                log_write('User search message:%s' % op_search, file_name)
                if op_search:
                    base.search_mid(op_search)
                else:
                    print('Enter at least 1 character to search.')
            elif op_num == '9':
                print(skin_msg)
            else:
                break

            input('Press enter to continue.')
    except Exception:
        log_write('[Fatal Error]\n%s' % format_exc(), file_name)

# TODO：Rewrite user interface, using dynamic refreshing mode
# TODO: Plot all songs at specific level
