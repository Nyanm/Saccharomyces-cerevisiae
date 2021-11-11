from cfg import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg import Timber
from ..uni_plot_tool import *

timber = Timber

# Reading config
song_folders = game_dir + '/music'
try:
    npy_path = local_dir + '/data/level_table.npy'
    level_table = np.load(npy_path)
except FileNotFoundError:
    timber.warning('level_table.npy not found, please check your file directory, '
                   'unless this is the first time you have started the application.\n'
                   'Press enter to continue.')
