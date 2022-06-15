import base64
from os import path, makedirs
import shutil

import ifstools

from util.local import local_dir
from util.logger import timber


def update_images(dependency: dict, game_dir: str):
    """
    dependency is a dict which has the following keys:
    is_ifs    : bool, option to enable ifs transformation
    ifs_ver   : list of int, ifs versions (of sdvx game)
    ifs_{gen} : list of str, specific ifs files of {gen}
    is_b64    : bool, option to enable base64 transformation, all b64 data is stored in data file under the genre folder
    b64       : list of str, b64 image sets
    b64_{set} : tuple, 1st values are variants of b64 coded str images, and 2nd values are file name after decoding
    is_tsp    : bool, option to enable file transportation
    tsp       : list of str, files need to be transported
    tsp_{file}: tuple, 1st values are suffixes after game_dir, and the 2nd values are suffixes after genre_dir
    """
    skin_name = dependency['skin_name']
    timber.debug(f'Update images for skin {skin_name}')
    archive_dir = local_dir + '/img_archive'
    if not path.exists(archive_dir):
        makedirs(archive_dir)
    genre_dir = archive_dir + '/%s' % skin_name
    if not path.exists(genre_dir):
        makedirs(genre_dir)
    timber.debug(f'Create skin image archive directory at [{genre_dir}]')

    # update ifs by using ifstools
    if dependency['is_ifs']:
        for version in dependency['ifs_ver']:
            cur_ver = str(version).zfill(2)
            ifs_list: list = dependency[f'ifs_{cur_ver}']
            ver_dir = f'{game_dir}/data/graphics/ver{cur_ver}'
            timber.debug(f'Get ifs list of gen{cur_ver}: {ifs_list}')
            timber.debug(f'Get ./contents/data/graphics/ver{cur_ver} path [{ver_dir}]')
            # transform ifs files
            for ifs_file in ifs_list:
                ifs_path = f'{ver_dir}/{ifs_file}.ifs'
                ifs_dst = f'{genre_dir}/{ifs_file}'
                if not path.exists(ifs_dst):
                    makedirs(ifs_dst)
                    timber.debug(f'Create directory for ifs {ifs_file} [{ifs_dst}]')
                if path.exists(ifs_path):
                    ifs = ifstools.IFS(ifs_path, super_disable=True, super_skip_bad=True)
                    ifs.extract(tex_only=True, path=ifs_dst, rename_dupes=True)
                    ifs.close()
                    timber.debug(f'Extract \'{ifs_file}\' in gen{cur_ver} complete')
                else:
                    timber.warning(f'ifs file \'{ifs_file}\' in gen{cur_ver} does not exist')
        timber.debug(f'Update ifs part for skin \'{skin_name}\' complete.')

    # decode base 64 files
    if dependency['is_b64']:
        b64_list = dependency['b64']
        timber.debug(f'Get b64 list: {b64_list}')
        # get b64 set
        for b64_set in b64_list:
            b64_val: list = dependency[f'b64_{b64_set}']
            b64_dst = f'{genre_dir}/{b64_set}'
            if not path.exists(b64_dst):
                makedirs(b64_dst)
                timber.debug(f'Create directory for b64 set \'{b64_set}\' [{b64_dst}]')
            # decode base64 file
            for item in b64_val:
                b64_raw, b64_file = item
                b64_path = f'{b64_dst}/{b64_file}'
                _file = open(b64_path, 'wb')
                _file.write(base64.b64decode(b64_raw))
                _file.close()
                timber.debug(f'Decode \'{b64_file}\' of b64 set \'{b64_set}\' at [{b64_path}]')
        timber.debug(f'Update base64 part for skin \'{skin_name}\' complete.')

    # ad hoc process for some specific files
    if dependency['is_tsp']:
        tsp_list = dependency['tsp']
        timber.debug(f'Get transport list: {tsp_list}')
        for tsp_index in tsp_list:
            tsp_val = f'tsp_{tsp_index}'
            tsp_src, tsp_dst = dependency[tsp_val]
            tsp_src = game_dir + tsp_src
            tsp_dst = genre_dir + tsp_dst
            timber.debug(f'Get transport file \'{tsp_val}\' source [{tsp_src}]')
            timber.debug(f'Get transport file \'{tsp_val}\' destination [{tsp_dst}]')
            tsp_dir = '/'.join(tsp_dst.split('/')[:-1])
            if not path.exists(tsp_dir):
                makedirs(tsp_dir)
                timber.debug(f'Create directory for file transportation \'{tsp_val}\' [{tsp_dir}]')
            shutil.copy(src=tsp_src, dst=tsp_dst)
        timber.debug(f'Update transportation part for skin \'{skin_name}\' complete.')

    timber.debug(f'Construct image archive for skin \'{skin_name}\' complete.')
