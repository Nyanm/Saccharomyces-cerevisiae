import re
import logging
import sys
from os import path

get_map_size = re.compile(r'map size+[^\n]*')
get_card_cfg = re.compile(r'card num+[^\n]*')
get_db_dir = re.compile(r'db path+[^\n]*')
get_game_dir = re.compile(r'game path+[^\n]*')
get_output = re.compile(r'output path+[^\n]*')
get_skin = re.compile(r'skin name+[^\n]*')
get_init_stat = re.compile(r'is initialized+[^\n]*')

# Turn off test mode when packing the program
test_mode = 1
if test_mode:
    local_dir = path.dirname(path.abspath(__file__)).replace('\\', '/')
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')

# Initialize logger
o_con = logging.StreamHandler()
o_con.setLevel(logging.WARNING)
o_file = logging.FileHandler(filename=local_dir + '/log.txt', mode='w')

fmt = logging.Formatter(fmt='%(asctime)s[%(filename)s-line%(lineno)s][%(levelname)s]:%(message)s', datefmt='[%H:%M:%S]')
o_con.setFormatter(fmt)
o_file.setFormatter(fmt)

timber = logging.getLogger('timber')
timber.setLevel(logging.INFO)
timber.addHandler(o_con)
timber.addHandler(o_file)

timber.info('test mode=%s' % test_mode)  # Initial logging

# Read config.txt
try:
    cfg_path = local_dir + '/config.txt'
    __raw_file = open(cfg_path, 'r')
except FileNotFoundError:
    logging.critical('config.txt not found, please check your file directory.')
    input()
    sys.exit(1)
cfg_data = ''
for __line in __raw_file.readlines():
    if __line[0] == '#':
        continue
    cfg_data += __line
__raw_file.close()

# Data cleaning
map_size = int(get_map_size.search(cfg_data).group()[9:])
card_num = get_card_cfg.search(cfg_data).group()[9:]
db_dir = get_db_dir.search(cfg_data).group()[8:].replace('\\', '/')
game_dir = get_game_dir.search(cfg_data).group()[10:].replace('\\', '/')
output = get_output.search(cfg_data).group()[12:].replace('\\', '/')
skin_name = get_skin.search(cfg_data).group()[10:]
is_init = get_init_stat.search(cfg_data)

timber.info('config.txt load complete.\n'
            'map size :%d\ncard num :%s\ndb dir   :%s\ngame dir :%s\noutput   :%s\nskin name:%s\nis init  :%s\n'
            % (map_size, card_num, db_dir, game_dir, output, skin_name, is_init is not None))
