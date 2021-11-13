from cfg_read import local_dir, map_size, card_num, db_dir, game_dir, output, skin_name, is_init
import base64
import ifstools
from os import path, listdir, makedirs
from hashlib import sha256
from cfg_read import local_dir


def file_2_b64(src: str, dst: str, name: str, write: str = 'w'):
    try:
        f = open(src, 'rb')
    except PermissionError:
        return
    b64_str = base64.b64encode(f.read())
    f.close()

    utf_str = '%s = "%s"\n\n' % (name, b64_str.decode('utf-8'))
    f = open(dst, write)
    f.write(utf_str)
    f.close()


def files_2_b64(folder: str, dst: str):
    for file in listdir(folder):
        file_path = '%s/%s' % (folder, file)
        name = path.splitext(file)[0].replace(' ', '_').replace('-', '_')
        file_2_b64(file_path, dst, name, write='a')


def convert_all(version: str, dst: str, abs_path: str = False, omit_folder: bool = False):
    if not path.exists(dst):
        makedirs(dst)
    ver_path = '%s/graphics/ver0%s/' % (game_dir, version)
    if abs_path:
        ver_path = abs_path + '/'
    for sg_path in listdir(ver_path):
        if sg_path.endswith('.ifs'):

            ifs_path = ver_path + sg_path
            if omit_folder:
                out_path = dst + '/'
            else:
                out_path = '%s/%s/' % (dst, sg_path[:-4])
            if not path.exists(out_path) and not omit_folder:
                makedirs(out_path)

            ifs = ifstools.IFS(ifs_path, super_disable=True, super_skip_bad=True)
            ifs.extract(tex_only=True, path=out_path, rename_dupes=True)
            ifs.close()


if __name__ == '__main__':
    """files_2_b64('C:/Users/nyanm/PycharmProjects/sdvx_remote/__img_archive/gen6/skill',
                local_dir + '/genre/gen6/data_plot_gen6.py')
    pass"""
    sh = sha256('C:\Arcade MUG\SDVX6\KentuckyFriedChicken\contents\data'.encode('utf-8'))
    print(sh.hexdigest())
