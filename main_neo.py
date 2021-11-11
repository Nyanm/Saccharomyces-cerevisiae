import random
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
        # Each line of music map should be
        # [is_recorded, mid, type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
        timber.info('Load data from sdvx@asphyxia.db')

        # Get raw data from db
        last_record, last_profile, last_skill, last_param = [], '', '', ''
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
                break
            elif line_type == 'profile':
                pass
            elif line_type == 'skill':
                pass
            elif line_type == 'param':
                pass


if __name__ == '__main__':
    sdvx = SDVX()

