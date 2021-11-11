import sys
import re
from os import path, listdir, remove, makedirs
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties
import pandas as pd
import seaborn as sns

get_map_size = re.compile(r'map size+[^\n]*')
get_card_cfg = re.compile(r'card num+[^\n]*')
get_db_dir = re.compile(r'db path+[^\n]*')
get_game_dir = re.compile(r'game path+[^\n]*')
get_output = re.compile(r'output path+[^\n]*')
get_skin = re.compile(r'skin name+[^\n]*')
get_init_stat = re.compile(r'is initialized+[^\n]*')

def log_write(content: str, writer: str):
    log.write('[%s][%s]:%s\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), writer, content))

test_mode = 1

if test_mode:
    local_dir = path.dirname(path.abspath(__file__)).replace('\\', '/')
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')

log = open(local_dir + '/log.txt', 'w', encoding='utf-8')

try:
    cfg_path = local_dir + '/config.txt'
    __raw_file = open(cfg_path, 'r')
except FileNotFoundError:
    log_write(r'config.txt not found, please check your file directory.', 'cfg_read.py')
    input(r'config.txt not found, please check your file directory.')
    sys.exit(1)
cfg_data = ''
for __line in __raw_file.readlines():
    if __line[0] == '#':
        continue
    cfg_data += __line
__raw_file.close()

map_size = int(get_map_size.search(cfg_data).group()[9:])
card_num = get_card_cfg.search(cfg_data).group()[9:]
db_dir = get_db_dir.search(cfg_data).group()[8:].replace('\\', '/')
game_dir = get_game_dir.search(cfg_data).group()[10:].replace('\\', '/')
output = get_output.search(cfg_data).group()[12:].replace('\\', '/')
skin_name = get_skin.search(cfg_data).group()[10:]
is_init = get_init_stat.search(cfg_data)

# pyinstaller -i sjf.ico -F main.py
