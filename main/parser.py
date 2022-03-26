import json
import time
import numpy as np

from cfg_read import cfg, local_dir


class ASPParser:
    def __init__(self):

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
            11: exscore: int,
        ]
        """

        # Load level table
        try:
            self.level_table = np.load(local_dir + '/data/level_table.npy')
            self.search_db = np.load(local_dir + '/data/search_db.npy')
            self.aka_db = np.load(local_dir + '/data/aka_db.npy', allow_pickle=True)
        except FileNotFoundError:
            raise


