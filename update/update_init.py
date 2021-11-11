from cfg import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg import Timber
from os import path, makedirs

from .update_db import update_db
from .update_aka import update_aka
from .update_img import update_img

timber = Timber()


def update():

    if not path.exists(local_dir + '/data/'):
        makedirs(local_dir + '/data/')

    # Set up level_table.npy and aka_db.npy
    update_db()
    if path.exists(local_dir + '/data/level_table.npy'):
        timber.info('generate level_table.npy successfully.')
    else:
        timber.error('Fail to generate level_table.npy.')
    if path.exists(local_dir + '/data/search_db.npy'):
        timber.info('generate search_db.npy successfully.')
    else:
        timber.error('Fail to generate search_db.npy.')

    update_aka()
    if path.exists(local_dir + '/data/aka_db.npy'):
        timber.info('generate aka_db.npy successfully.')
    else:
        timber.error('Fail to generate aka_db.npy.')

    update_img()
