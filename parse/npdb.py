import sys

import numpy as np

from utli.dir import local_dir
from utli.logger import timber

try:
    aka_db = np.load(local_dir + '/data/aka_db.npy', allow_pickle=True)
    level_table = np.load(local_dir + '/data/level_table.npy')
    search_db = np.load(local_dir + '/data/search_db.npy')
    timber.info('Load aka_db, level_table, search_db from ./data')
except FileNotFoundError:
    timber.error('Critical npy files not found, please delete the last line of config.cfg and restart.')
    sys.exit(1)
