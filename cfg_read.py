import sys
import re
from os import path
import time

get_map_size = re.compile(r'map size+[^\n]*')
get_card_cfg = re.compile(r'card num+[^\n]*')
get_db_dir = re.compile(r'db path+[^\n]*')
get_game_dir = re.compile(r'game path+[^\n]*')
get_output = re.compile(r'output path+[^\n]*')
get_skin = re.compile(r'skin name+[^\n]*')
get_init_stat = re.compile(r'is initialized+[^\n]*')

test_mode = 1

if test_mode:
    local_dir = path.dirname(path.abspath(__file__)).replace('\\', '/')
else:
    local_dir = path.dirname(path.abspath(sys.executable)).replace('\\', '/')

log = open(local_dir + '/log.txt', 'w', encoding='utf-8')


def get_cfg() -> tuple:
    """
    Uniform config reader, all paths have converted "\\" into "/".
    :return: a tuple which includes:
             map_size<int>   default as 2000
             card_num<str>   just a 16 bit hex card number
             local_dir<str>  path of executable program
             db_dir<str>     abstract position of sdvx@asphyxia.db, no need to operate
             game_dir<str>   path like .../KFC-**********/contents/data, need to add lower directory in order to use
             output<str>     a folder where you want to save your picture
             skin_name<str>  name of skin, namely plot_{skin_name}.py, it has a corresponding folder in ./img_archive/
    """
    try:
        cfg_path = local_dir + '/config.txt'
        raw_file = open(cfg_path, 'r')
    except FileNotFoundError:
        log_write(r'config.txt not found, please check your file directory.', 'cfg_read.py')
        input(r'config.txt not found, please check your file directory.')
        sys.exit(1)
    cfg_data = ''
    for line in raw_file.readlines():
        if line[0] == '#':
            continue
        cfg_data += line
    raw_file.close()

    map_size = int(get_map_size.search(cfg_data).group()[9:])
    card_num = get_card_cfg.search(cfg_data).group()[9:]
    db_dir = get_db_dir.search(cfg_data).group()[8:].replace('\\', '/')
    game_dir = get_game_dir.search(cfg_data).group()[10:].replace('\\', '/')
    output = get_output.search(cfg_data).group()[12:].replace('\\', '/')
    skin_name = get_skin.search(cfg_data).group()[10:]
    is_init = get_init_stat.search(cfg_data)

    return map_size, card_num, local_dir, db_dir, game_dir, output, skin_name, is_init


def log_write(content: str, writer: str):
    log.write('[%s][%s]:%s\n' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), writer, content))


# pyinstaller -i sjf.ico -F main.py
