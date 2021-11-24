from cfg_read import local_dir, cfg
from .common import jis_2_utf, amend_jis
from xml.etree.cElementTree import parse
import numpy as np
import os


aka_range = 500


def update_aka():
    jis_path = cfg.game_dir + '/others/akaname_parts.xml'
    utf_path = local_dir + '/data/akaname_parts.xml'

    # Set up akaname_parts encoded with UTF-8
    jis_2_utf(jis_path, utf_path)

    # Get database for akaname
    tree = parse(utf_path)
    root = tree.getroot()

    aka_map = []
    for index in range(aka_range):
        try:
            aka_id = int(root[index].attrib['id'])
            aka_name = amend_jis(root[index][0].text)
            aka_map.append([aka_id, aka_name])
        except IndexError:
            break

    # Save akaname database
    try:
        os.remove(utf_path)
    except FileNotFoundError:
        pass
    aka_map = aka_map[1:]
    aka_map = np.array(aka_map)
    np.save(local_dir + '/data/aka_db.npy', aka_map)
