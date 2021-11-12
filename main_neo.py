import sys
import os
import re
import json
from copy import deepcopy
import numpy as np

from cfg import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg import Timber
from update.update_init import update
from genre.gen6 import main_plot_gen6
from genre.gen5 import main_plot_gen5

# Dictionary for vf calculation
clear_factor = {1: 0.5, 2: 1.0, 3: 1.02, 4: 1.05, 5: 1.10}
grade_factor = {1: 0.80, 2: 0.82, 3: 0.85, 4: 0.88, 5: 0.91, 6: 0.94, 7: 0.97, 8: 1.00, 9: 1.02, 10: 1.05}

# Look up table for crew, only support crew with LIVE-2D
crew_id = {116: '0001', 95: '0002', 96: '0003', 100: '0004', 101: '0005', 102: '0006', 103: '0007', 104: '0008',
           105: '0009', 106: '0010', 107: '0011', 109: '0012', 112: '0013', 113: '0014', 117: '0015', 118: '0016',
           119: '0017', 120: '0018', 121: '0019'}

timber = Timber()
skin_dict = {'gen6': main_plot_gen6, 'gen5': main_plot_gen5}


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
        last_record = []
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
                last_record = [True, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf]
                self.music_map[music_index] = last_record

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
            self.akaname = 'よろしくお願いします'
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
                        (self.user_name, self.ap_card, self.aka_index, self.skill, self.crew_id))
        except AttributeError:
            timber.error('Profile/Skill/Crew data not found, '
                         'make sure you have at least played once (and saved successfully).')

    def search_mid(self, search_str: str):
        result_list = []
        timber.info('Searching "%s"' % search_str)
        for index in range(1, map_size):
            if re.search(search_str, self.search_db[index], re.I):
                result_list.append(index)

        if not result_list:
            print('未能搜索到结果  No search result found')
            timber.info('Search failed.')
            return

        search_res = ('%d result(s) found:\n\n|No  |MID   |[Name]  [Artist]\n' % len(result_list))
        for index in range(len(result_list)):
            __mid = result_list[index]
            search_res += '|%-4d|%-4d  |[%s]  [%s]\n' %\
                          (index + 1, __mid, self.level_table[__mid][1], self.level_table[__mid][2])

        timber.info(search_res)
        print('共搜索到%d个结果  %s' % (len(result_list), search_res))


if __name__ == '__main__':
    sdvx = SDVX()
    sdvx.search_mid('FAITHFUL')
