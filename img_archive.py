import os

from cfg_read import *
import ifstools


# ifs = ifstools.IFS('C:/Arcade MUG/SDVX6/SDVX tools/dump_files/achievement.ifs')
# ifs.extract(tex_only=True, path='C:/Arcade MUG/SDVX6/SDVX tools/dump_files')


def py_decompress(from_path, to_path):
    pass


def init_img_archive(ing_dict: dict):
    version = ing_dict['version']
    ifs_list = ing_dict['ifs_list']
    for content in ifs_list:
        con_path = ing_dict[content]



def convert_all(version: str, dst: str, abs_path: str = False, omit_folder: bool = False):
    if not os.path.exists(dst):
        os.makedirs(dst)
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
            if not os.path.exists(out_path) and not omit_folder:
                os.makedirs(out_path)

            ifs = ifstools.IFS(ifs_path, super_disable=True, super_skip_bad=True)
            ifs.extract(tex_only=True, path=out_path, rename_dupes=True)
            ifs.close()


if __name__ == '__main__':
    convert_all('5', 'C:/Arcade MUG/SDVX6/SDVX tools/card',
                abs_path='C:/Arcade MUG/SDVX6/KentuckyFriedChicken/contents/data/graphics/chara_card', omit_folder=True)
