from utli.cfg_read import cfg
# from hashlib import sha256
from os import path, listdir
from ..universal import *
import time

"""
Initialization
"""

# Reading config
song_folders = cfg.game_dir + '/music'
img_archive = local_dir + '/img_archive/gen6'

"""
Pre-define
"""
# Quick color table
color_white = (245, 245, 245)
color_l_white = (255, 255, 255)
color_black = (61, 61, 61)
color_gray = (154, 154, 154)
color_l_gray = (210, 210, 210)
color_d_gray = (122, 122, 122)
color_gold = (246, 222, 128)
color_l_blue = (147, 255, 254)
color_d_blue = (0, 62, 102)
color_yellow = (239, 176, 74)

# Definitive field for some dictionary(or they work as tuple)
clear_img = {1: 'crash', 2: 'comp', 3: 'comp_ex', 4: 'uc', 5: 'puc'}
clear_table = {1: 'FAILED', 2: 'NC', 3: 'HC', 4: 'UC', 5: 'PUC'}
clear_palette = ('#FFFFFF', '#32936F', '#69A297', '#A5668B', '#E83F6F', '#FFBF00')
clear_legend = ('N/A', 'CRASH', 'NC', 'HC', 'UC', 'PUC')

grade_img = {1: 'd', 2: 'c', 3: 'b', 4: 'a', 5: 'a_plus', 6: 'aa', 7: 'aa_plus', 8: 'aaa', 9: 'aaa_plus', 10: 's'}
grade_table = {1: 'D', 2: 'C', 3: 'B', 4: 'A', 5: 'A+', 6: 'AA', 7: 'AA+', 8: 'AAA', 9: 'AAA+', 10: 'S'}
grade_palette = ('#FFFFFF', '#CFD2CD', '#A6A2A2', '#847577',
                 '#66C9A3', '#32936F', '#D296B9', '#A5668B', '#E36E94', '#E83F6F', '#FFBF00',)
grade_legend = ('N/A', 'D', 'C', 'B', 'A', 'A+', 'AA', 'AA+', 'AAA', 'AAA+', 'S')

level_palette = ('#F7FFF7', '#073B4C', '#118AB2', '#06D6A0', '#FFD166', '#EF476F')

diff_table = [['NOV', 'ADV', 'EXH', '', 'MXM'] for _ in range(5)]
diff_table[0][3], diff_table[1][3], diff_table[2][3], diff_table[3][3], diff_table[4][3] = \
    'INF', 'GRV', 'HVN', 'VVD', 'XCD'
diff_text_table = {1: 'nov', 2: 'adv', 3: 'exh', 4: 'inf', 5: 'grv', 6: 'hvn', 7: 'vvd', 8: 'mxm'}

vf_level = (0.0, 10.0, 12.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 24.0)
vf_color = (color_white, (193, 139, 73), (48, 73, 157), (245, 189, 26), (83, 189, 181), (200, 22, 30), (237, 179, 202),
            (234, 234, 233), (248, 227, 165), (198, 59, 55), (108, 76, 148))

# Fonts
font_DFHS = img_archive + '/font/DFHSMaruGothic_W4_reform.ttf'
font_unipace = img_archive + '/font/unispace_bd.ttf'
font_continuum = img_archive + '/font/continuum_medium.ttf'

# Little privilege for developers
staff_hash = 'b3e46c3a84f6e042ef5f3d934b746ded23a3961d0774293ec2fbe3b42e0ada47'

"""
Functions
"""


def get_vf_level(vf: float, is_color: bool = False, is_darker: bool = False):
    if vf < 0 or vf > 24:
        return
    vf_grade = 10
    for index in range(len(vf_level)):
        if vf < vf_level[index]:
            vf_grade = index
            break
    vf_interval = (vf_level[vf_grade] - vf_level[vf_grade - 1]) / 4
    vf_stars = int(np.floor((vf - vf_level[vf_grade - 1]) / vf_interval)) + 1

    if is_color:
        color = vf_color[vf_grade]
        if is_darker:
            return tuple(np.array(color) * 2 // 3)
        return color

    return vf_grade, vf_stars


def get_jacket_path(mid: int, m_type: int, size: str = False) -> str:
    mid = str(mid).zfill(4)
    for song_folder in listdir(song_folders):
        if song_folder.startswith(mid):
            song_path = ('%s/%s/' % (song_folders, song_folder))
            m_index = m_type + 1
            while m_index:
                if path.exists('%sjk_%s_%d.png' % (song_path, mid, m_index)):
                    if size:
                        return '%sjk_%s_%d_%s.png' % (song_path, mid, m_index, size)
                    return '%sjk_%s_%d.png' % (song_path, mid, m_index)
                m_index -= 1
            if size:
                return cfg.game_dir + '/data/graphics/jk_dummy_%s.png' % size
            else:
                return cfg.game_dir + '/data/graphics/jk_dummy_s.png'


def get_jacket(mid: int, m_type: int, size: str = False):
    jk_path = get_jacket_path(mid, m_type, size)
    jk = cv2.imread(jk_path, cv2.IMREAD_UNCHANGED)
    try:
        if jk.shape[2] == 3:
            jk = add_alpha(jk)
        return jk
    except IndexError:
        jk = cv2.merge((jk, jk, jk))
        jk = add_alpha(jk)
        return jk


def get_diff(m_type: int, inf_ver: str) -> str:
    try:
        return diff_table[int(inf_ver) - 2][m_type]
    except IndexError:
        return 'UNK'


def get_ap_card(ap_card: int) -> str:
    ap_card = str(ap_card).zfill(4)
    card_file = 'ap_'
    card_ver, is_r, is_s = int(ap_card[0]) + 1, (ap_card[1] == '5'), (ap_card[1] == '9')
    if card_ver == 1:
        pass
    else:
        card_file += ('0%s_' % card_ver)
    if is_r:
        card_file += ('R%s' % ap_card[2:].zfill(4))
    elif is_s:
        card_file += ('S%s' % ap_card[2:].zfill(4))
    else:
        card_file += ap_card[1:].zfill(4)
    return cfg.game_dir + '/graphics/ap_card/%s.png' % card_file


def get_overall_vf(music_b50: list) -> float:
    vol_force = 0.0
    for record in music_b50:
        if record[0]:
            vol_force += record[9]
        else:
            break
    vol_force = vol_force / 50
    return vol_force


def get_bpm_str(bpm_max: np.str, bpm_min: np.str) -> str:
    if bpm_max[-2:] == '00':
        bpm_max = bpm_max[:-2]
    else:
        bpm_max = str(int(bpm_max) / 100)
    if bpm_min[-2:] == '00':
        bpm_min = bpm_min[:-2]
    else:
        bpm_min = str(int(bpm_min) / 100)

    if bpm_max == bpm_min:
        return bpm_max
    else:
        return '%s-%s' % (bpm_min, bpm_max)


def load_clear(refactor: float or int) -> list:
    clear_no = cv2.imread(img_archive + '/ms_sel/mark_no.png', cv2.IMREAD_UNCHANGED)
    clear_cr = cv2.imread(img_archive + '/ms_sel/mark_crash.png', cv2.IMREAD_UNCHANGED)
    clear_nc = cv2.imread(img_archive + '/ms_sel/mark_comp.png', cv2.IMREAD_UNCHANGED)
    clear_hc = cv2.imread(img_archive + '/ms_sel/mark_comp_ex.png', cv2.IMREAD_UNCHANGED)
    clear_uc = cv2.imread(img_archive + '/ms_sel/mark_uc.png', cv2.IMREAD_UNCHANGED)
    clear_puc = cv2.imread(img_archive + '/ms_sel/mark_puc.png', cv2.IMREAD_UNCHANGED)

    clear_list = [clear_no, clear_cr, clear_nc, clear_hc, clear_uc, clear_puc]
    if refactor:
        for index in range(6):
            if clear_list[index] is not None:
                clear_list[index] = \
                    cv2.resize(clear_list[index], dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return clear_list


def load_grade(refactor: float or int) -> list:
    grade_a = cv2.imread(img_archive + '/ms_sel/grade_a.png', cv2.IMREAD_UNCHANGED)
    grade_ap = cv2.imread(img_archive + '/ms_sel/grade_a_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aa = cv2.imread(img_archive + '/ms_sel/grade_aa.png', cv2.IMREAD_UNCHANGED)
    grade_aap = cv2.imread(img_archive + '/ms_sel/grade_aa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aaa = cv2.imread(img_archive + '/ms_sel/grade_aaa.png', cv2.IMREAD_UNCHANGED)
    grade_aaap = cv2.imread(img_archive + '/ms_sel/grade_aaa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_b = cv2.imread(img_archive + '/ms_sel/grade_b.png', cv2.IMREAD_UNCHANGED)
    grade_c = cv2.imread(img_archive + '/ms_sel/grade_c.png', cv2.IMREAD_UNCHANGED)
    grade_d = cv2.imread(img_archive + '/ms_sel/grade_d.png', cv2.IMREAD_UNCHANGED)
    grade_s = cv2.imread(img_archive + '/ms_sel/grade_s.png', cv2.IMREAD_UNCHANGED)

    grade_list = [None, grade_d, grade_c, grade_b, grade_a, grade_ap,
                  grade_aa, grade_aap, grade_aaa, grade_aaap, grade_s]
    if refactor:
        for index in range(11):
            if grade_list[index] is not None:
                grade_list[index] = \
                    cv2.resize(grade_list[index], dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return grade_list


def load_level(refactor: float or int) -> list:
    level_nov = cv2.imread(img_archive + '/psd_level/level_small_nov.png', cv2.IMREAD_UNCHANGED)
    level_adv = cv2.imread(img_archive + '/psd_level/level_small_adv.png', cv2.IMREAD_UNCHANGED)
    level_exh = cv2.imread(img_archive + '/psd_level/level_small_exh.png', cv2.IMREAD_UNCHANGED)
    level_inf = cv2.imread(img_archive + '/psd_level/level_small_inf.png', cv2.IMREAD_UNCHANGED)
    level_grv = cv2.imread(img_archive + '/psd_level/level_small_grv.png', cv2.IMREAD_UNCHANGED)
    level_hvn = cv2.imread(img_archive + '/psd_level/level_small_hvn.png', cv2.IMREAD_UNCHANGED)
    level_vvd = cv2.imread(img_archive + '/psd_level/level_small_vvd.png', cv2.IMREAD_UNCHANGED)
    level_xcd = cv2.imread(img_archive + '/psd_level/level_small_xcd.png', cv2.IMREAD_UNCHANGED)
    level_mxm = cv2.imread(img_archive + '/psd_level/level_small_mxm.png', cv2.IMREAD_UNCHANGED)

    level_list = \
        [level_nov, level_adv, level_exh, None, level_mxm, level_inf, level_grv, level_hvn, level_vvd, level_xcd]
    if refactor:
        for level in level_list:
            if level:
                cv2.resize(level, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return level_list


def load_skill(card_img: np.array, skill: int, dis_resize: bool = False) -> np.array:
    skill_img = cv2.imread(img_archive + '/skill/skill_' + str(skill).zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    if not dis_resize:
        skill_ratio = card_img.shape[1] / skill_img.shape[1]
        skill_img = cv2.resize(skill_img, dsize=None, fx=skill_ratio, fy=skill_ratio, interpolation=cv2.INTER_AREA)
    return skill_img


def load_vf(vf: float, is_small: bool = False, is_text: bool = False):
    vf_grade, vf_stars = get_vf_level(vf)
    if is_text:
        vf_text = cv2.imread(img_archive + '/force/font_force_%s.png' % str(vf_grade).zfill(2), cv2.IMREAD_UNCHANGED)
        return vf_text
    else:
        if is_small:
            vf_img = cv2.imread(img_archive + '/force/em6_s%s_i_eab.png' % str(vf_grade).zfill(2), cv2.IMREAD_UNCHANGED)
        else:
            vf_img = cv2.imread(img_archive + '/force/em6_%s_i_eab.png' % str(vf_grade).zfill(2), cv2.IMREAD_UNCHANGED)
        return vf_img


def load_frame() -> tuple:
    top_left = cv2.imread(img_archive + '/frame/top_left.png', cv2.IMREAD_UNCHANGED)
    top_right = cv2.imread(img_archive + '/frame/top_right.png', cv2.IMREAD_UNCHANGED)
    btm_left = cv2.imread(img_archive + '/frame/btm_left.png', cv2.IMREAD_UNCHANGED)
    btm_right = cv2.imread(img_archive + '/frame/btm_right.png', cv2.IMREAD_UNCHANGED)

    side_top = cv2.imread(img_archive + '/frame/top_orange.png', cv2.IMREAD_UNCHANGED)
    side_right = side_left = cv2.imread(img_archive + '/frame/bar.png', cv2.IMREAD_UNCHANGED)
    side_bottom = cv2.imread(img_archive + '/frame/btm_orange.png', cv2.IMREAD_UNCHANGED)
    return [top_left, top_right, btm_left, btm_right], [side_top, side_right, side_bottom, side_left]


def load_bar(name: str, is_bg: bool = False) -> list:
    left = cv2.imread(img_archive + '/bar/%s_left.png' % name, cv2.IMREAD_UNCHANGED)
    bar = cv2.imread(img_archive + '/bar/%s_bar.png' % name, cv2.IMREAD_UNCHANGED)
    right = cv2.imread(img_archive + '/bar/%s_right.png' % name, cv2.IMREAD_UNCHANGED)
    if is_bg:
        bg = cv2.imread(img_archive + '/bar/%s_bg.png' % name, cv2.IMREAD_UNCHANGED)
    else:
        bg = None
    return [left, bar, right, bg]


def generate_hex_bg(size: tuple, par_a: float = -0.55, par_c: float = 1.1) -> np.array:
    bg_hex = cv2.imread(img_archive + '/bg/bg_hex.png', cv2.IMREAD_UNCHANGED)
    bg_element = np.zeros(bg_hex.shape, dtype=bg_hex.dtype)
    png_superimpose(bg_element, bg_hex)
    bg = bg_duplicator(bg_element, size[0], size[1])
    parabola_gradient(bg, a=par_a, c=par_c)
    return bg


def generate_std_profile(profile: list, vf: float) -> np.array:
    user_name, ap_card, aka_name, skill, crew_id = profile

    profile_box = cv2.imread(img_archive + '/play_data/box_playdata.png', cv2.IMREAD_UNCHANGED)
    data_box = cv2.imread(img_archive + '/play_data/box_playdata2.png', cv2.IMREAD_UNCHANGED)
    bl_line = cv2.imread(img_archive + '/play_data/blpass_bg.png', cv2.IMREAD_UNCHANGED)
    bl_pass = cv2.imread(img_archive + '/play_data/blpass_on.png', cv2.IMREAD_UNCHANGED)
    crew = cv2.imread(img_archive + '/psd_crew/psd_crew_%s.png' % crew_id, cv2.IMREAD_UNCHANGED)
    appeal_card = cv2.imread(get_ap_card(ap_card), cv2.IMREAD_UNCHANGED)
    skill_img = load_skill(appeal_card, skill, dis_resize=True)
    vf_icon = load_vf(vf, is_small=True)
    vf_text = load_vf(vf, is_text=True)
    vf_raw = cv2.imread(img_archive + '/force/font_force_m.png', cv2.IMREAD_UNCHANGED)
    vf_star = cv2.imread(img_archive + '/force/star_gold_i_eab.png', cv2.IMREAD_UNCHANGED)

    appeal_card = cv2.resize(appeal_card, dsize=None, fx=0.86, fy=0.86, interpolation=cv2.INTER_AREA)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.42, fy=0.42, interpolation=cv2.INTER_AREA)
    vf_icon = cv2.resize(vf_icon, dsize=None, fx=0.41, fy=0.41, interpolation=cv2.INTER_AREA)
    vf_star = cv2.resize(vf_star, dsize=None, fx=0.17, fy=0.17, interpolation=cv2.INTER_AREA)

    profile_y, profile_x, chn = profile_box.shape
    crew_y, crew_x, chn = crew.shape
    bg = np.zeros((crew_y + 10, profile_x, 4), dtype=np.uint8)
    box_margin = crew_y - profile_y + 10

    png_superimpose(bg, profile_box, (box_margin, 0))
    png_superimpose(bg, bl_line, (box_margin + 73, 479))
    png_superimpose(bg, crew, (2, profile_x - crew_x - 9))
    png_superimpose(bg, bl_pass, (box_margin + 152, 554))
    png_superimpose(bg, data_box, (box_margin + 47, 207))
    png_superimpose(bg, appeal_card, (box_margin + 60, 52))
    """
    # It's just so ugly that I have no choice but withdraw this tiny privilege of developer :(
    if sha256(game_dir.encode('utf-8')).hexdigest() == staff_hash:
        staff = cv2.imread(img_archive + '/ap_floor/sdvx_staff_s.png', cv2.IMREAD_UNCHANGED)
        png_superimpose(bg, staff, (box_margin + 60, 43))
    """
    png_superimpose(bg, skill_img, (box_margin + 189, 225))
    png_superimpose(bg, vf_icon, (box_margin + 174, 385))
    png_superimpose(bg, vf_raw, (box_margin + 182, 421))
    png_superimpose(bg, vf_text, (box_margin + 192, 421))

    star_y, star_x, chn = vf_star.shape
    star_interval = 1
    star_num = get_vf_level(vf)[1]
    star_margin = (2 * star_interval + star_x) * (4 - star_num) // 2
    star_grid = Anchor(bg, 'star grid', (box_margin + 219, 389 + star_margin))
    star_grid.creat_grid((0, star_num), (0, star_x + 2 * star_interval))
    star_anc = AnchorImage(bg, 'star', vf_star, (0, 0), star_grid)

    for index in range(star_num):
        star_anc.set_grid((0, index))
        star_anc.plot()

    blank_layer = np.ones((crew_y + 10, profile_x, 3), dtype=np.uint8) * 245
    text_layer = Image.fromarray(blank_layer)
    text_layer.putalpha(1)
    pen = ImageDraw.Draw(text_layer)

    aka_font = ImageFont.truetype(font_DFHS, 18, encoding='utf-8', index=0)
    name_font = ImageFont.truetype(font_continuum, 34, encoding='utf-8', index=0)
    vf_font = ImageFont.truetype(font_continuum, 21, encoding='utf-8', index=0)
    time_font = ImageFont.truetype(font_DFHS, 14, encoding='utf-8', index=0)
    pen.text((218, 146), aka_name, color_white, aka_font)
    pen.text((218, 174), user_name, color_white, name_font)
    pen.text((218, 227), 'Asphyxia CORE', color_white, aka_font)
    pen.text((436, 295), '%.3f' % vf, color_white, vf_font)
    pen.text((602, 291), time.strftime('%a %Y/%m/%d %H: %M', time.localtime()), color_white, time_font)

    text_layer = np.array(text_layer)
    png_superimpose(bg, text_layer)

    return bg


def generate_mini_profile(profile: list, vf: float, vf_specific: list = None) -> np.array:
    user_name, ap_card, aka_name, skill, crew_id = profile

    profile_box = cv2.imread(img_archive + '/play_data_small/box_result_mine.png', cv2.IMREAD_UNCHANGED)
    appeal_card = cv2.imread(get_ap_card(ap_card), cv2.IMREAD_UNCHANGED)
    skill_img = load_skill(appeal_card, skill, dis_resize=True)
    vf_icon = load_vf(vf, is_small=True)
    vf_star = cv2.imread(img_archive + '/force/star_gold_i_eab.png', cv2.IMREAD_UNCHANGED)
    vf_raw = cv2.imread(img_archive + '/force/font_force_s.png', cv2.IMREAD_UNCHANGED)

    appeal_card = cv2.resize(appeal_card, dsize=None, fx=0.70, fy=0.70, interpolation=cv2.INTER_AREA)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.32, fy=0.32, interpolation=cv2.INTER_AREA)
    vf_icon = cv2.resize(vf_icon, dsize=None, fx=0.29, fy=0.29, interpolation=cv2.INTER_AREA)
    vf_star = cv2.resize(vf_star, dsize=None, fx=0.10, fy=0.10, interpolation=cv2.INTER_AREA)

    bg = profile_box
    blank_layer = np.ones((profile_box.shape[0], profile_box.shape[1], 3), dtype=np.uint8) * 255
    text_layer = Image.fromarray(blank_layer)
    text_layer.putalpha(1)
    pen = ImageDraw.Draw(text_layer)

    png_superimpose(bg, appeal_card, (37, 24))
    png_superimpose(bg, skill_img, (125, 160))
    png_superimpose(bg, vf_icon, (114, 278))
    png_superimpose(bg, vf_raw, (119, 291))

    star_y, star_x, chn = vf_star.shape
    star_interval = 1
    star_num = get_vf_level(vf)[1]
    star_margin = (2 * star_interval + star_x) * (4 - star_num) // 2
    star_grid = Anchor(bg, 'star grid', (146, 282 + star_margin))
    star_grid.creat_grid((0, star_num), (0, star_x + 2 * star_interval))
    star_anc = AnchorImage(bg, 'stars', vf_star, (0, 0), star_grid)

    for index in range(star_num):
        star_anc.set_grid((0, index))
        star_anc.plot()

    if vf_specific:
        vfs, rank = vf_specific[0], vf_specific[1]
        vf_text = load_vf(vfs, is_text=True)
        vf_raw = cv2.imread(img_archive + '/force/font_force_m.png', cv2.IMREAD_UNCHANGED)

        png_superimpose(bg, vf_raw, (102, 380))
        png_superimpose(bg, vf_text, (112, 380))

        rank_font = ImageFont.truetype(font_DFHS, 18, encoding='utf-8', index=0)
        vfs_font = ImageFont.truetype(font_continuum, 26, encoding='utf-8', index=0)
        pen.text((397, 135), '#', color_l_white, rank_font)
        pen.text((415, 135), str(rank), color_l_white, rank_font)

        vf_layer = np.ones((profile_box.shape[0], profile_box.shape[1], 3), dtype=np.uint8) * 48
        vf_layer = Image.fromarray(vf_layer)
        vf_layer.putalpha(1)
        vf_pen = ImageDraw.Draw(vf_layer)
        vf_pen.text((397, 148), '%.3f' % vfs, rgb_2_bgr(get_vf_level(vfs, is_color=True)), vfs_font)
        vf_layer = np.array(vf_layer)
        png_superimpose(bg, vf_layer)

    vf_font = ImageFont.truetype(font_continuum, 16, encoding='utf-8', index=0)
    aka_font = ImageFont.truetype(font_DFHS, 18, encoding='utf-8', index=0)
    name_font = ImageFont.truetype(font_continuum, 27, encoding='utf-8', index=0)
    ser_font = ImageFont.truetype(font_DFHS, 16, encoding='utf-8', index=0)

    pen.text((316, 132), '%.3f' % vf, color_l_white, vf_font)
    pen.text((153, 33), aka_name, color_l_white, aka_font)
    pen.text((153, 57), user_name, color_l_white, name_font)
    if vf_specific:
        time_str = vf_specific[2]
        pen.text((46, 214), 'Played at %s' % time_str, color_white, ser_font)
    else:
        pen.text((46, 214), 'Asphyxia CORE', color_white, ser_font)

    text_layer = np.array(text_layer)
    png_superimpose(bg, text_layer)

    return bg
