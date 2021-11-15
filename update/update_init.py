from cfg_read import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
from cfg_read import Timber
from os import path, makedirs, system
from time import sleep


from .update_db import update_db
from .update_aka import update_aka
from .update_img import update_img

timber = Timber('update_init.py')


def update():

    timber.warning('Since you have updated your game (or simply the maiden run of the program), '
                   'the program is going to generate some relative data.\n'
                   'It may take some time to finish, press enter to continue.')

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
    if path.exists(local_dir + '/img_archive/%s' % skin_name):
        timber.info('(maybe) generate image archive successfully.')
    else:
        timber.error('Fail to generate image archive.')

    # add initialized sign
    __raw_file = open(local_dir + '/config.cfg', 'a')
    __raw_file.write('is initialized=True\n')
    __raw_file.close()

    sleep(0.2)
    timber.info_clog('\nUpdate complete. Press enter to continue.')
    system('cls')
