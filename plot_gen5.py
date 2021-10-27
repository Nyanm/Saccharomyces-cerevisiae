import cv2
from PIL import Image, ImageDraw, ImageFont
from os import listdir
from cfg_read import *
from numpy import array, load

file_name = 'plot_gen5.py'

map_size, card_num__, local_dir, db_dir, game_dir, output, skin_name, is_init = get_cfg()
song_folders = game_dir + '/music'
try:
    npy_path = local_dir + '/data/level_table.npy'
    level_table = load(npy_path)
except FileNotFoundError:
    log_write('level_table.npy not found, please check your file directory, '
              'unless this is the first time you have started the application.', file_name)
    input('level_table.npy not found, please check your file directory, '
          'unless this is the first time you have started the application.\n'
          'Press enter to continue.')
    pass

img_archive = local_dir + '/img_archive/gen5/'
if not path.exists(img_archive):
    input(r'Image archive is missing, please check your file directory.')
    sys.exit(1)
