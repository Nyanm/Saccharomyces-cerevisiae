import sys
import os
from copy import deepcopy

from cfg import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg import timber
from update import update_init

from genre.gen6 import main_plot_gen6
from genre.gen5 import main_plot_gen5
skin_dict = {'gen6': main_plot_gen6, 'gen5': main_plot_gen5}


class SDVX:

    def __init__(self):

        try:
            self.plot_skin = skin_dict[skin_name]
        except KeyError:
            timber.critical('Invalid skin name, please check your configurations.')


if __name__ == '__main__':
    sdvx = SDVX
