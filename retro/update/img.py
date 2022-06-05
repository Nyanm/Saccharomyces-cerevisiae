from os import path, makedirs
import shutil

import ifstools

from .common import decode_b64

from retro.utli.dir import local_dir


def update_img(game_dir, skin_name):
    def update_ifs(ifs_list: list, __version: str):
        ver_path = '%s/graphics/ver0%s/' % (game_dir, __version)

        for ifs_file in ifs_list:
            ifs_path = ver_path + '%s.ifs' % ifs_file
            ifs_dst = genre_path + '/%s' % ifs_file
            if not path.exists(ifs_dst):
                makedirs(ifs_dst)
            ifs = ifstools.IFS(ifs_path, super_disable=True, super_skip_bad=True)
            ifs.extract(tex_only=True, path=ifs_dst, rename_dupes=True)
            ifs.close()

    def update_b64(b64_list: list, folder_name: str):
        b64_dst = genre_path + '/%s' % folder_name
        if not path.exists(b64_dst):
            makedirs(b64_dst)

        for b64_tuple in b64_list:
            b64_file, b64_name = b64_tuple
            b64_path = '%s/%s' % (b64_dst, b64_name)
            decode_b64(b64_file, b64_path)

    def update_transport(trans_loc: list):
        trans_src = game_dir + trans_loc[0]
        trans_dst = genre_path + trans_loc[1]
        trans_path = '/'.join(trans_dst.split('/')[:-1])
        if not path.exists(trans_path):
            makedirs(trans_path)
        shutil.copy(trans_src, trans_dst)

    archive_path = local_dir + '/img_archive'
    if not path.exists(archive_path):
        makedirs(archive_path)
    genre_path = archive_path + '/%s' % skin_name
    if not path.exists(genre_path):
        makedirs(genre_path)

    dependency_dict = {'gen5': retro.update.data.gen5.dependency, 'gen6': retro.update.data.gen6.dependency}

    dependency = dependency_dict[skin_name].dependency

    # Update ifs using ifstools
    if dependency['is_ifs']:
        for version in dependency['version']:
            update_ifs(dependency['ifs0%s' % version], version)

    # Decode base64 files
    if dependency['is_b64']:
        for b64_index in dependency['b64']:
            update_b64(dependency['b64_%s' % b64_index], b64_index)

    # Ad hoc process for some specific files
    if dependency['is_transport']:
        for trans_index in dependency['transport']:
            update_transport(dependency['transport_%s' % trans_index])
