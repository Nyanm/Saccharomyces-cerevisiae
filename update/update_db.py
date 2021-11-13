from cfg_read import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg_read import decode_b64, jis_2_utf
from xml.etree.cElementTree import parse
import numpy as np
import os
import csv
from .update_db_data import csv_data


# WHY USING SHIFT-JIS???!!!
def update_db():
    jis_path = game_dir + '/others/music_db.xml'
    utf_path = local_dir + '/data/music_db.xml'

    # Set up music_db encoded with UTF-8
    jis_2_utf(jis_path, utf_path)

    # Get level information from xml, then saved as npy file
    tree = parse(utf_path)
    root = tree.getroot()
    music_map = [[''] * 22 for _ in range(map_size)]
    search_map = [[''] * 3 for _ in range(map_size)]

    for index in range(map_size):
        try:
            # Fill up each line of level_table.npy
            mid = int(root[index].attrib['id'])
            name = root[index][0][1].text \
                .replace("驫", "ā").replace("骭", "ü").replace("驩", "Ø").replace("罇", "ê").replace("曩", "è") \
                .replace("齷", "é").replace("騫", "á").replace("曦", "à").replace("龕", "€").replace("趁", "Ǣ") \
                .replace("蹇", "₂").replace("彜", "ū").replace("雋", "Ǜ").replace("隍", "Ü").replace("鬻", "♃") \
                .replace("鬥", "Ã").replace("鬆", "Ý").replace("齶", "♡").replace("齲", "❤").replace("躔", "★") \
                .replace('釁', '🍄').replace('頽', 'ä').replace('黻', '*')
            artist = root[index][0][3].text \
                .replace("驫", "ā").replace("骭", "ü").replace("驩", "Ø").replace("罇", "ê").replace("曩", "è") \
                .replace("齷", "é").replace("騫", "á").replace("曦", "à").replace("龕", "€").replace("趁", "Ǣ") \
                .replace("蹇", "₂").replace("彜", "ū").replace("雋", "Ǜ").replace("隍", "Ü").replace("鬻", "♃") \
                .replace("鬥", "Ã").replace("鬆", "Ý").replace("齶", "♡").replace("齲", "❤").replace("躔", "★") \
                .replace('釁', '🍄').replace('頽', 'ä').replace('黻', '*')
            bpm_max = int(root[index][0][6].text)
            bpm_min = int(root[index][0][7].text)
            version = int(root[index][0][13].text)
            inf_ver = int(root[index][0][15].text)

            nov_lv = int(root[index][1][0][0].text)
            nov_ill = root[index][1][0][1].text
            nov_eff = root[index][1][0][2].text
            adv_lv = int(root[index][1][1][0].text)
            adv_ill = root[index][1][1][1].text
            adv_eff = root[index][1][1][2].text
            exh_lv = int(root[index][1][2][0].text)
            exh_ill = root[index][1][2][1].text
            exh_eff = root[index][1][2][2].text
            inf_lv = int(root[index][1][3][0].text)
            inf_ill = root[index][1][3][1].text
            inf_eff = root[index][1][3][2].text
            try:
                mxm_lv = int(root[index][1][4][0].text)
                mxm_ill = root[index][1][4][1].text
                mxm_eff = root[index][1][4][2].text
            except IndexError:
                mxm_lv = 0
                mxm_ill = 'dummy'
                mxm_eff = 'dummy'
            music_map[int(mid)] = [mid, name, artist, bpm_max, bpm_min, version, inf_ver, nov_lv, nov_ill,
                                   nov_eff, adv_lv, adv_ill, adv_eff, exh_lv, exh_ill, exh_eff, inf_lv,
                                   inf_ill, inf_eff, mxm_lv, mxm_ill, mxm_eff]

            # Fill up each line of aka_db.npy
            music_ascii = root[index][0][5].text.replace('_', ' ')
            search_map[int(mid)] = [name, artist, music_ascii]

        except IndexError:
            break

    # Save level table
    try:
        os.remove(utf_path)
    except FileNotFoundError:
        pass
    music_map = np.array(music_map)
    np.save(local_dir + '/data/level_table.npy', music_map)

    # Decompress csv data from update_db_data.py
    csv_path = local_dir + '/data/raw_search_db.csv'
    decode_b64(csv_data, csv_path)

    temp_list = []
    search_csv = csv.reader(open(local_dir + '/data/raw_search_db.csv', encoding='utf-8'))
    __index = 0
    for csv_record in search_csv:
        temp_list.append(' '.join(csv_record))

    # Set up search database
    search_list = [' ' for _ in range(map_size)]
    search_list[:len(temp_list)] = temp_list
    for index in range(map_size):
        if search_list[index][0] is ' ':
            search_list[index] = ' '.join(search_map[index])

    # Save search database
    search_list = np.array(search_list)
    np.save(local_dir + '/data/search_db.npy', search_list)
