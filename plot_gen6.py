from os import listdir

import numpy as np
from matplotlib.ticker import MaxNLocator
import pandas as pd
import seaborn as sns

from cfg_read import *
from uni_plot_tool import *

file_name = 'plot_gen6.py'
sns.set_style('darkgrid')
sns.set_context(rc={'lines.linewidth': 2})

map_size, card_num__, local_dir, db_dir, game_dir, output, skin_name, is_init = get_cfg()
song_folders = game_dir + '/music'
try:
    npy_path = local_dir + '/data/level_table.npy'
    level_table = np.load(npy_path)
except FileNotFoundError:
    log_write('level_table.npy not found, please check your file directory, '
              'unless this is the first time you have started the application.', file_name)
    input('level_table.npy not found, please check your file directory, '
          'unless this is the first time you have started the application.\n'
          'Press enter to continue.')
    pass

img_archive = local_dir + '/img_archive/gen6/'
if not path.exists(img_archive):
    input(r'Image archive is missing, please check your file directory.')
    sys.exit(1)

font_DFHS = img_archive + 'font/DFHSMaruGothic-W4-reform.ttc'
font_unipace = img_archive + 'font/unispace bd.ttf'

color_white = (245, 245, 245)
color_black = (61, 61, 61)
color_gray = (154, 154, 154)
color_l_gray = (210, 210, 210)
color_gold = (246, 222, 128)
color_l_blue = (115, 203, 215)

clear_img = {'1': 'crash', '2': 'comp', '3': 'comp_ex', '4': 'uc', '5': 'puc'}
clear_table = {'1': 'FAILED', '2': 'NC', '3': 'HC', '4': 'UC', '5': 'PUC'}
color_list = ('#909090', '#32936F', '#69A297', '#A5668B', '#E83F6F', '#FFBF00')
clear_legend = ('No Record', 'Track Crash', 'Normal Clear', 'Hard Clear', 'Ultimate Chain', 'Perfect Ultimate Chain')

grade_img = {'1': 'd', '2': 'c', '3': 'b', '4': 'a', '5': 'a_plus', '6': 'aa', '7': 'aa_plus', '8': 'aaa',
             '9': 'aaa_plus', '10': 's'}
grade_table = {'1': 'D', '2': 'C', '3': 'B', '4': 'A', '5': 'A+',
               '6': 'AA', '7': 'AA+', '8': 'AAA', '9': 'AAA+', '10': 'S'}
grade_color_table = ('#909090', '#CFD2CD', '#A6A2A2', '#847577',
                     '#66C9A3', '#32936F', '#D296B9', '#A5668B', '#E36E94', '#E83F6F', '#FFBF00',)
grade_legend = ('N/A', 'D', 'C', 'B', 'A', 'A+', 'AA', 'AA+', 'AAA', 'AAA+', 'S')


def get_vf_property(vf: float, is_darker: bool = False, is_level: bool = False) -> tuple or int:
    if vf < 0:
        level = 0
        color = color_white
    elif vf < 10:
        level = 1
        color = (193, 139, 73)
    elif vf < 12:
        level = 2
        color = (48, 73, 157)
    elif vf < 14:
        level = 3
        color = (245, 189, 26)
    elif vf < 15:
        level = 4
        color = (83, 189, 181)
    elif vf < 16:
        level = 5
        color = (200, 22, 30)
    elif vf < 17:
        level = 6
        color = (237, 179, 202)
    elif vf < 18:
        level = 7
        color = (234, 234, 233)
    elif vf < 19:
        level = 8
        color = (248, 227, 165)
    elif vf < 20:
        level = 9
        color = (198, 59, 55)
    else:
        level = 10
        color = (108, 76, 148)
    if is_darker:
        return tuple(np.array(color) * 2 // 3)
    if is_level:
        return level
    return color


def get_jacket(mid: str, m_type: str, is_small: bool = False) -> str:
    mid = mid.zfill(4)
    target_jk = ('jk_%s_%d.png' % (mid, (int(m_type) + 1)))
    backup_jk = ('jk_%s_1.png' % mid)
    dummy_jk_path = game_dir + '/data/graphics/jk_dummy.png'
    if is_small:
        target_jk = ('jk_%s_%d_s.png' % (mid, (int(m_type) + 1)))
        backup_jk = ('jk_%s_1_s.png' % mid)
        dummy_jk_path = game_dir + '/data/graphics/jk_dummy_s.png'
    for song_folder in listdir(song_folders):
        if song_folder.startswith(mid):
            song_path = ('%s/%s/' % (song_folders, song_folder))
            if path.exists(song_path + target_jk):
                return song_path + target_jk
            elif path.exists(song_path + backup_jk):
                return song_path + backup_jk
    return dummy_jk_path


def get_diff(m_type: str, inf_ver: str) -> str:
    diff_table = [['NOV', 'ADV', 'EXH', '', 'MXM'] for _ in range(4)]
    diff_table[0][3], diff_table[1][3], diff_table[2][3], diff_table[3][3] = 'INF', 'GRV', 'HVN', 'VVD'
    try:
        return diff_table[int(inf_ver) - 2][int(m_type)]
    except IndexError:
        return 'UNK'


def get_ap_card(ap_card: str) -> str:
    card_file = 'ap_'
    card_ver, is_r, is_s = int(ap_card[0]) + 1, (ap_card[1] == '5'), (ap_card[1] == '9')
    if card_ver == 1:
        pass
    else:
        card_file += ('0%s_' % card_ver)
    if is_r:
        card_file += ('R%s' % ap_card[1:].zfill(4))
    elif is_s:
        card_file += ('S%s' % ap_card[1:].zfill(4))
    else:
        card_file += ap_card[1:].zfill(4)
    return game_dir + '/graphics/ap_card/%s.png' % card_file


def get_overall_vf(music_b50: list) -> float:
    vol_force = 0.0
    for record in music_b50:
        if record[0]:
            vol_force += int(record[-1] * 10) / 1000
        else:
            break
    return vol_force


def load_marks(refactor: float = False) -> list:
    mark_no = cv2.imread(img_archive + 'mark/mark_no.png', cv2.IMREAD_UNCHANGED)
    mark_cr = cv2.imread(img_archive + 'mark/mark_crash.png', cv2.IMREAD_UNCHANGED)
    mark_nc = cv2.imread(img_archive + 'mark/mark_comp.png', cv2.IMREAD_UNCHANGED)
    mark_hc = cv2.imread(img_archive + 'mark/mark_comp_ex.png', cv2.IMREAD_UNCHANGED)
    mark_uc = cv2.imread(img_archive + 'mark/mark_uc.png', cv2.IMREAD_UNCHANGED)
    mark_puc = cv2.imread(img_archive + 'mark/mark_puc.png', cv2.IMREAD_UNCHANGED)

    mark_list = [mark_no, mark_cr, mark_nc, mark_hc, mark_uc, mark_puc]
    if refactor:
        for index in range(6):
            if mark_list[index] is not None:
                mark_list[index] = \
                    cv2.resize(mark_list[index], dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return mark_list


def load_grade(refactor: float = False) -> list:
    grade_a = cv2.imread(img_archive + 'grade/grade_a.png', cv2.IMREAD_UNCHANGED)
    grade_ap = cv2.imread(img_archive + 'grade/grade_a_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aa = cv2.imread(img_archive + 'grade/grade_aa.png', cv2.IMREAD_UNCHANGED)
    grade_aap = cv2.imread(img_archive + 'grade/grade_aa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aaa = cv2.imread(img_archive + 'grade/grade_aaa.png', cv2.IMREAD_UNCHANGED)
    grade_aaap = cv2.imread(img_archive + 'grade/grade_aaa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_b = cv2.imread(img_archive + 'grade/grade_b.png', cv2.IMREAD_UNCHANGED)
    grade_c = cv2.imread(img_archive + 'grade/grade_c.png', cv2.IMREAD_UNCHANGED)
    grade_d = cv2.imread(img_archive + 'grade/grade_d.png', cv2.IMREAD_UNCHANGED)
    grade_s = cv2.imread(img_archive + 'grade/grade_s.png', cv2.IMREAD_UNCHANGED)

    grade_list = [None, grade_d, grade_c, grade_b, grade_a, grade_ap,
                  grade_aa, grade_aap, grade_aaa, grade_aaap, grade_s]
    if refactor:
        for index in range(11):
            if grade_list[index] is not None:
                grade_list[index] = \
                    cv2.resize(grade_list[index], dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return grade_list


def load_level(refactor: float = False) -> list:
    level_nov = cv2.imread(img_archive + 'level/level_small_nov.png', cv2.IMREAD_UNCHANGED)
    level_adv = cv2.imread(img_archive + 'level/level_small_adv.png', cv2.IMREAD_UNCHANGED)
    level_exh = cv2.imread(img_archive + 'level/level_small_exh.png', cv2.IMREAD_UNCHANGED)
    level_inf = cv2.imread(img_archive + 'level/level_small_inf.png', cv2.IMREAD_UNCHANGED)
    level_grv = cv2.imread(img_archive + 'level/level_small_grv.png', cv2.IMREAD_UNCHANGED)
    level_hvn = cv2.imread(img_archive + 'level/level_small_hvn.png', cv2.IMREAD_UNCHANGED)
    level_vvd = cv2.imread(img_archive + 'level/level_small_vvd.png', cv2.IMREAD_UNCHANGED)
    level_mxm = cv2.imread(img_archive + 'level/level_small_mxm.png', cv2.IMREAD_UNCHANGED)

    level_list = [level_nov, level_adv, level_exh, None, level_mxm, level_inf, level_grv, level_hvn, level_vvd]
    if refactor:
        for level in level_list:
            if level:
                cv2.resize(level, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return level_list


def generate_hex_bg(size: tuple, par_a: float = -0.55, par_c: float = 1.08):
    bg_hex = cv2.imread(img_archive + 'bg/hex.png', cv2.IMREAD_UNCHANGED)
    bg_element = np.zeros(bg_hex.shape, dtype=bg_hex.dtype)
    png_superimpose(bg_element, bg_hex)
    bg = bg_duplicator(bg_element, size[0], size[1])
    parabola_gradient(bg, a=par_a, c=par_c)
    return bg


def plot_single(record: list, profile: list):
    """
    Plot function for single record
    :param record:  a list of [mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf]
                    all of them are strings, except vf is a float
    :param profile: a list of [user_name, aka_name, ap_card, skill], all strings
    :return:        image stored as numpy array
    """
    mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf = record
    user_name, aka_name, ap_card, skill = profile
    diff = get_diff(m_type, inf_ver)
    real_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(m_time) / 1000))

    bg = cv2.imread(img_archive + 'bg/bg_template.png')

    # Plot appeal card
    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    card_img = cv2.resize(card_img, dsize=None, fx=0.48, fy=0.48, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, card_img, [22, 111])

    # Plot skill
    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.38, fy=0.38, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, skill_img, [79, 203])

    # Plot jacket
    jk_path = get_jacket(mid, m_type)
    jk = cv2.imread(jk_path)
    bg[155:455, 126:426] = jk

    # Get bpm string
    bpm_h, bpm_l = level_table[int(mid)][3], level_table[int(mid)][4]
    if bpm_h[-2:] == '00':
        bpm_h = int(int(bpm_h) / 100)
    else:
        bpm_h = int(bpm_h) / 100
    if bpm_l[-2:] == '00':
        bpm_l = int(int(bpm_l) / 100)
    else:
        bpm_l = int(bpm_l) / 100
    if bpm_h == bpm_l:
        bpm = str(bpm_h)
    else:
        bpm = str(bpm_l) + "~" + str(bpm_h)

    # Plot level box
    level_box = cv2.imread(img_archive + 'level/level_small_' + diff.lower() + '.png', cv2.IMREAD_UNCHANGED)
    level_box = cv2.resize(level_box, dsize=None, fx=0.824, fy=0.824, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, level_box, [474, 352])

    # Get artist string
    artist = level_table[int(mid)][2]

    # Plot clear mark
    mark = cv2.imread(img_archive + 'mark/mark_' + clear_img[clear] + '.png', cv2.IMREAD_UNCHANGED)
    mark = cv2.resize(mark, dsize=None, fx=0.941, fy=0.941, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, mark, [517, 418])

    # Get effector and illustrator string
    ill, eff = level_table[int(mid)][int(m_type) * 3 + 8], level_table[int(mid)][int(m_type) * 3 + 9]

    # Plot score
    score_x, is_zero = 2, True
    score = score.zfill(8)
    h_score, l_score = score[:4], score[4:8]

    for num in h_score:
        score_x += (58 + 1)
        if num != '0':
            is_zero = False
        num_img = cv2.imread(img_archive + 'number/num_score_' + num + '.png', cv2.IMREAD_UNCHANGED)
        png_superimpose(bg, num_img, [690, score_x], is_zero)

    score_x += 56
    for num in l_score:
        if num != '0':
            is_zero = False
        num_img = cv2.imread(img_archive + 'number/num_mmscore_' + num + '.png', cv2.IMREAD_UNCHANGED)
        png_superimpose(bg, num_img, [698, score_x], is_zero)
        score_x += 50

    # Plot grade
    grade_bg = cv2.imread(img_archive + 'grade/box_medal.png', cv2.IMREAD_UNCHANGED)
    grade_bg = cv2.resize(grade_bg, dsize=None, fx=0.9, fy=0.9, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, grade_bg, [775, 94])

    grade_png = cv2.imread(img_archive + 'grade/grade_' + grade_img[grade] + '.png', cv2.IMREAD_UNCHANGED)
    grade_png = cv2.resize(grade_png, dsize=None, fx=0.41, fy=0.41, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, grade_png, [783, 104])

    # Plot all characters
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(bg)
    pen = ImageDraw.Draw(pil_img)

    name_font = ImageFont.truetype(font_DFHS, 34, encoding='utf-8', index=0)
    pen.text((202, 30), user_name, color_white, font=name_font)

    bpm_font = ImageFont.truetype(font_unipace, 16, encoding='utf-8')
    pen.text((166, 473), bpm, color_white, font=bpm_font)

    name_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
    name_uni = length_uni(name_font, name, 335)
    artist_uni = length_uni(name_font, artist, 335)
    pen.text((69, 517), name_uni, color_white, font=name_font)
    pen.text((69, 560), artist_uni, color_white, font=name_font)

    eff_font = ImageFont.truetype(font_DFHS, 15, encoding='utf-8', index=0)
    eff_uni = length_uni(eff_font, eff, 250)
    ill_uni = length_uni(eff_font, ill, 250)
    pen.text((222, 612), eff_uni, color_white, font=eff_font)
    pen.text((222, 648), ill_uni, color_white, font=eff_font)

    lv_font = ImageFont.truetype(font_unipace, 12, encoding='utf-8')
    pen.text((418, 478), lv, color_white, font=lv_font)

    time_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
    pen.text((216, 777), 'VOLFORCE', color_white, font=time_font)
    pen.text((216, 815), real_time, color_white, font=time_font)

    vf_font = ImageFont.truetype(font_unipace, 20, encoding='utf-8')
    pen.text((369, 776), '%.3f' % (vf / 2), get_vf_property(vf / 2), font=vf_font)

    bg = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # cv2.imshow('test', bg)
    # cv2.waitKey(0)

    # Get recent text message
    msg = ''
    msg += ('Played at %s\n' % real_time)
    msg += ('%s%-2s  %s\n' % (diff, lv, name))
    msg += ('%-9s%-6s%-5s\n' % (score, grade_table[grade], clear_table[clear]))
    msg += ('VF:%.3f\n' % vf)

    print(msg)

    cv2.imwrite('%s/%s_Recent.png' % (output, user_name), bg, params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

    print('Plot successfully.')


def plot_b50(music_map: list, profile: list):
    """
    Plot function for best 50 records
    :param music_map: a list contains all music records, each line of music_map should be:
                      [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
                      all of them are strings, except vf is a float
    :param profile:   a list of [card_num, user_name, aka_name, ap_card, skill], all strings
    :return:          image stored as numpy array
    """
    card_num, user_name, aka_name, ap_card, skill = profile
    music_map.sort(key=lambda x: x[10], reverse=True)
    music_b50 = music_map[:50]

    # Get overall volforce
    vol_force = get_overall_vf(music_b50)
    log_write('Get overall volforce complete', file_name)

    # Load image files
    bg = cv2.imread(img_archive + 'bg/B50_bg.png', cv2.IMREAD_UNCHANGED)

    level_nov = cv2.imread(img_archive + 'level/level_small_nov.png', cv2.IMREAD_UNCHANGED)
    level_adv = cv2.imread(img_archive + 'level/level_small_adv.png', cv2.IMREAD_UNCHANGED)
    level_exh = cv2.imread(img_archive + 'level/level_small_exh.png', cv2.IMREAD_UNCHANGED)
    level_inf = cv2.imread(img_archive + 'level/level_small_inf.png', cv2.IMREAD_UNCHANGED)
    level_grv = cv2.imread(img_archive + 'level/level_small_grv.png', cv2.IMREAD_UNCHANGED)
    level_hvn = cv2.imread(img_archive + 'level/level_small_hvn.png', cv2.IMREAD_UNCHANGED)
    level_vvd = cv2.imread(img_archive + 'level/level_small_vvd.png', cv2.IMREAD_UNCHANGED)
    level_mxm = cv2.imread(img_archive + 'level/level_small_mxm.png', cv2.IMREAD_UNCHANGED)
    level_list = [level_nov, level_adv, level_exh, '', level_mxm, level_inf, level_grv, level_hvn, level_vvd]

    mark_refactor = 0.58
    mark_cr = cv2.imread(img_archive + 'mark/bg_mark_crash.png', cv2.IMREAD_UNCHANGED)
    mark_cr = cv2.resize(mark_cr, dsize=None, fx=mark_refactor, fy=mark_refactor, interpolation=cv2.INTER_AREA)
    mark_nc = cv2.imread(img_archive + 'mark/bg_mark_comp.png', cv2.IMREAD_UNCHANGED)
    mark_nc = cv2.resize(mark_nc, dsize=None, fx=mark_refactor, fy=mark_refactor, interpolation=cv2.INTER_AREA)
    mark_hc = cv2.imread(img_archive + 'mark/bg_mark_comp_ex.png', cv2.IMREAD_UNCHANGED)
    mark_hc = cv2.resize(mark_hc, dsize=None, fx=mark_refactor, fy=mark_refactor, interpolation=cv2.INTER_AREA)
    mark_uc = cv2.imread(img_archive + 'mark/bg_mark_uc.png', cv2.IMREAD_UNCHANGED)
    mark_uc = cv2.resize(mark_uc, dsize=None, fx=mark_refactor, fy=mark_refactor, interpolation=cv2.INTER_AREA)
    mark_puc = cv2.imread(img_archive + 'mark/bg_mark_puc.png', cv2.IMREAD_UNCHANGED)
    mark_puc = cv2.resize(mark_puc, dsize=None, fx=mark_refactor, fy=mark_refactor, interpolation=cv2.INTER_AREA)
    mark_list = ['', mark_cr, mark_nc, mark_hc, mark_uc, mark_puc]

    grade_refactor = 0.42
    grade_a = cv2.imread(img_archive + 'grade/bg_grade_a.png', cv2.IMREAD_UNCHANGED)
    grade_a = cv2.resize(grade_a, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_ap = cv2.imread(img_archive + 'grade/bg_grade_a_plus.png', cv2.IMREAD_UNCHANGED)
    grade_ap = cv2.resize(grade_ap, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_aa = cv2.imread(img_archive + 'grade/bg_grade_aa.png', cv2.IMREAD_UNCHANGED)
    grade_aa = cv2.resize(grade_aa, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_aap = cv2.imread(img_archive + 'grade/bg_grade_aa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aap = cv2.resize(grade_aap, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_aaa = cv2.imread(img_archive + 'grade/bg_grade_aaa.png', cv2.IMREAD_UNCHANGED)
    grade_aaa = cv2.resize(grade_aaa, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_aaap = cv2.imread(img_archive + 'grade/bg_grade_aaa_plus.png', cv2.IMREAD_UNCHANGED)
    grade_aaap = cv2.resize(grade_aaap, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_b = cv2.imread(img_archive + 'grade/bg_grade_b.png', cv2.IMREAD_UNCHANGED)
    grade_b = cv2.resize(grade_b, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_c = cv2.imread(img_archive + 'grade/bg_grade_c.png', cv2.IMREAD_UNCHANGED)
    grade_c = cv2.resize(grade_c, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_d = cv2.imread(img_archive + 'grade/bg_grade_d.png', cv2.IMREAD_UNCHANGED)
    grade_d = cv2.resize(grade_d, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_s = cv2.imread(img_archive + 'grade/bg_grade_s.png', cv2.IMREAD_UNCHANGED)
    grade_s = cv2.resize(grade_s, dsize=None, fx=grade_refactor, fy=grade_refactor, interpolation=cv2.INTER_AREA)
    grade_list = ['', grade_d, grade_c, grade_b, grade_a, grade_ap, grade_aa, grade_aap, grade_aaa, grade_aaap, grade_s]

    log_write('# Load image files complete', file_name)

    # Plot images about user profile
    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    card_img = cv2.resize(card_img, dsize=None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, card_img, [44, 827])

    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.42, fy=0.42, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, skill_img, [233, 827])

    vf_level = get_vf_property(vol_force, is_level=True)
    force_img = cv2.imread(img_archive + 'vf/em6_' + str(vf_level).zfill(2) + '_i_eab.png', cv2.IMREAD_UNCHANGED)
    force_img = cv2.resize(force_img, dsize=None, fx=0.34, fy=0.34, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, force_img, [123, 1000])

    # Stipulate relative distance of each elements, due to the OpenCV, the correlate system is (y, x)
    absolute, y_pace, x_pace = (323, 40), 136, 770
    pos_jk, pos_level, pos_mark, pos_grade = (8, 17), (14, 144), (61, 147), (61, 202)

    # Plot image parts
    for index in range(50):
        is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf = music_b50[index]
        if not is_recorded:
            break
        else:
            pass
        base_pos = [absolute[0] + (y_pace * (index // 2)), absolute[1] + (x_pace * (index % 2))]

        # Plot jacket
        jk_path = get_jacket(mid, m_type, True)
        jk = cv2.imread(jk_path, cv2.IMREAD_UNCHANGED)
        jk = add_alpha(jk)
        simple_plot(bg, jk, base_pos, relative=pos_jk)

        # Plot level box
        if m_type == '3':
            level_box = level_list[int(m_type) + int(inf_ver)]
        else:
            level_box = level_list[int(m_type)]
        simple_plot(bg, level_box, base_pos, relative=pos_level)

        # Plot small icons
        mark_icon = mark_list[int(clear)]
        simple_plot(bg, mark_icon, base_pos, relative=pos_mark)

        grade_icon = grade_list[int(grade)]
        simple_plot(bg, grade_icon, base_pos, relative=pos_grade)

    log_write('Image plot complete', file_name)

    # Initialize fonts
    user_font = ImageFont.truetype(font_DFHS, 40, encoding='utf-8', index=0)
    id_font = ImageFont.truetype(font_DFHS, 24, encoding='utf-8', index=0)
    vol_font = ImageFont.truetype(font_DFHS, 30, encoding='utf-8', index=0)
    vol_num_font = ImageFont.truetype(font_unipace, 28, encoding='utf-8')
    ceil_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)
    ceil_num_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')

    level_font = ImageFont.truetype(font_unipace, 15, encoding='utf-8')
    name_font = ImageFont.truetype(font_DFHS, 26, encoding='utf-8', index=0)
    score_h_font = ImageFont.truetype(font_DFHS, 44, encoding='utf-8', index=0)
    score_l_font = ImageFont.truetype(font_DFHS, 32, encoding='utf-8', index=0)
    vf_str_font = ImageFont.truetype(font_DFHS, 32, encoding='utf-8', index=0)
    vf_num_font = ImageFont.truetype(font_unipace, 26, encoding='utf-8')
    rank_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)

    h_size, l_size = score_h_font.getsize('0')[0], score_l_font.getsize('0')[0]
    log_write('Fonts initialization complete', file_name)

    # Plot all character strings
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(bg)
    pen = ImageDraw.Draw(pil_img)

    # Plot strings of user profile, due to the PIL, the correlate system is (x, y)
    abs_user, abs_id, abs_vol, abs_vol_num, abs_ceil, abs_floor, abs_ceil_num, abs_floor_num = \
        (1020, 55), (1020, 100), (1135, 160), (1344, 161), (1260, 212), (1234, 237), (1344, 214), (1344, 239)
    pos_level_num, pos_name, pos_h_score, pos_vf, pos_vf_num, pos_rank = \
        (221, 19), (271, 14), (271, 63), (510, 73), (570, 75), (700, 93)

    # Check validity of ceil and floor
    if music_b50[0][0]:
        ceil_num = music_b50[0][-1] / 2
    else:
        ceil_num = 0.0
    if music_b50[-1][0]:
        floor_num = music_b50[-1][-1] / 2
    else:
        floor_num = 0.0

    pen.text(abs_user, user_name, color_white, font=user_font)
    pen.text(abs_id, 'ID  ' + card_num, color_white, font=id_font)
    pen.text(abs_vol, 'VOLFORCE', color_white, font=vol_font)
    pen.text(abs_vol_num, ('%.3f' % vol_force), get_vf_property(vol_force), font=vol_num_font)
    pen.text(abs_ceil, 'CEIL', color_white, font=ceil_font)
    pen.text(abs_floor, 'FLOOR', color_white, font=ceil_font)
    pen.text(abs_ceil_num, ('%.3f' % ceil_num), get_vf_property(ceil_num), font=ceil_num_font)
    pen.text(abs_floor_num, ('%.3f' % floor_num), get_vf_property(floor_num), font=ceil_num_font)

    # Plot strings of music records
    def str_plot(text: str, str_font, pos: tuple, color: tuple, length: int = 0, relative: tuple = (0, 0)):
        x, y = pos[0] + relative[0], pos[1] + relative[1]
        if length:
            text = length_uni(str_font, text, length)
        pen.text((x, y), text, color, font=str_font)

    for index in range(50):
        is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf = music_b50[index]
        if not is_recorded:
            break
        base_pos = (absolute[1] + (x_pace * (index % 2)), absolute[0] + (y_pace * (index // 2)))

        # Plot level
        str_plot(lv, level_font, base_pos, color_white, relative=pos_level_num)

        # Plot name
        str_plot(name, name_font, base_pos, color_black, length=450, relative=pos_name)

        # Plot score(both higher bit and lower bit)
        score = score.zfill(8)
        h_score, l_score = score[:4], score[4:8]
        zero_flag = 1
        num_color = color_gray
        x_score = pos_h_score[0]
        for num in h_score:
            if num != '0' and zero_flag:
                num_color = color_black
                zero_flag = 0
            str_plot(num, score_h_font, base_pos, num_color, relative=(x_score, pos_h_score[1]))
            x_score += h_size

        y_l_score = pos_h_score[1] + 10
        for num in l_score:
            if num != '0' and zero_flag:
                num_color = color_black
                zero_flag = 0
            str_plot(num, score_l_font, base_pos, num_color, relative=(x_score, y_l_score))
            x_score += l_size

        # Plot VF("VF" and the vf value)
        str_plot('VF', vf_str_font, base_pos, color_black, relative=pos_vf)
        str_plot(('%.3f' % (vf / 2)), vf_num_font, base_pos, get_vf_property(vf / 2, is_darker=True),
                 relative=pos_vf_num)

        # Plot rank
        str_plot('#%d' % (index + 1), rank_font, base_pos, color_black, relative=pos_rank)
    log_write('Characters plot complete', file_name)

    bg = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # Get b50 message
    msg = ''
    msg += ('----------------VOLFORCE %.3f----------------\n' % vol_force)
    msg += 'No.  VF      DIFF   SCORE    RANK  LHT  NAME\n'
    for index in range(50):
        diff = get_diff(music_b50[index][2], music_b50[index][9])
        msg += ('#%-4d%.3f  %s%-2s  %-9s%-6s%-5s%s\n' % ((index + 1), music_b50[index][10], diff,
                                                         music_b50[index][8], music_b50[index][3],
                                                         clear_table[music_b50[index][4]],
                                                         grade_table[music_b50[index][5]], music_b50[index][7]))
    print(msg)
    log_write('Text message generate complete.\n%s' % msg, file_name)

    cv2.imwrite('%s/%s_B50.png' % (output, user_name), bg, params=[cv2.IMWRITE_PNG_COMPRESSION, 3])
    log_write('Plot at %s/%s_B50.png' % (output, user_name), file_name)
    print('Plot successfully.')


def plot_summary_legacy(level_summary: np.array, profile: list):
    """
    Plot function for summarizing the level 17, 18, 19, 20 charts
    :param level_summary: a list of statistics, each line of level summary should be:
                          [NC, HC, UC, PUC, AAA, AAA+, S, sum], all ints
    :param profile:       a list of [card_num, user_name, aka_name, ap_card, skill], all strings
    :return:              image stored as numpy array
    """

    card_num, user_name, aka_name, ap_card, skill = profile
    x_pace, y_pace = 89, 93
    bg = cv2.imread(img_archive + 'bg/bg_summary.png')
    msg = ''
    msg += '----------------Level Summary----------------\n' \
           'Level    NC      HC      UC      PUC     ||    AAA     AAA+    S\n'

    # Plot user profile images
    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    card_img = cv2.resize(card_img, dsize=None, fx=0.48, fy=0.48, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, card_img, [22, 111])

    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.38, fy=0.38, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, skill_img, [79, 203])

    # Plot all characters
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(bg)
    pen = ImageDraw.Draw(pil_img)

    name_font = ImageFont.truetype(font_DFHS, 34, encoding='utf-8', index=0)
    num_font = ImageFont.truetype(font_unipace, 27, encoding='utf-8')
    s_num_font = ImageFont.truetype(font_unipace, 15, encoding='utf-8')
    sum_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')
    date_font = ImageFont.truetype(font_DFHS, 15, encoding='utf-8', index=0)

    pen.text((202, 30), user_name, color_white, font=name_font)

    x_index = 156
    for index in range(17, 21):
        nc, hc, uc, puc, aaa, aaa_plus, s, sum_ = level_summary[index]
        msg += ('lv.%d    ' % index)
        msg += ('%-8s%-8s%-8s%-8s||    %-8s%-8s%-8s\n' %
                (int(nc), int(hc), int(uc), int(puc), int(aaa), int(aaa_plus), int(s)))

        y_index = 246
        for sub_index in range(0, 4):
            mark_all = sum(level_summary[index][sub_index: 4])
            if mark_all == level_summary[index][7]:
                text_color = color_gold
            else:
                text_color = color_white
            pen.text((x_index, y_index), str(int(level_summary[index][sub_index])), text_color, font=num_font)
            if sub_index < 3:
                pen.text((x_index, y_index + 32), '(%s)' % str(int(mark_all)), text_color, font=s_num_font)
            y_index += y_pace
        y_index -= 61
        pen.text((x_index + 30, y_index), '/%s' % str(int(level_summary[index][7])), color_white, font=sum_font)

        y_index += 91
        for sub_index in range(4, 7):
            level_all = sum(level_summary[index][sub_index: 7])
            if level_all == level_summary[index][7]:
                text_color = color_gold
            else:
                text_color = color_white
            pen.text((x_index, y_index), str(int(level_summary[index][sub_index])), text_color, font=num_font)
            if sub_index < 6:
                pen.text((x_index, y_index + 32), '(%s)' % str(int(level_all)), text_color, font=s_num_font)
            y_index += (y_pace + 2)

        y_index -= 61
        pen.text((x_index + 30, y_index), '/%s' % str(int(level_summary[index][7])), color_white, font=sum_font)

        x_index += x_pace

    # Plot level summary date
    real_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))

    pen.text((50, 943), 'Ploted at %s by Saccharomyces cerevisiae' % real_time, color_white, font=date_font)
    bg = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # cv2.imshow('test', bg)
    # cv2.waitKey(0)

    print(msg)
    log_write('Text message generate complete.\n%s' % msg, file_name)

    cv2.imwrite('%s/%s_Summary.png' % (output, user_name), bg, params=[cv2.IMWRITE_PNG_COMPRESSION, 3])
    log_write('Plot at %s/%s_Summary.png' % (output, user_name), file_name)
    print('Plot successfully.')


def plot_summary_legacy_of_lunatic_kingdom(music_map: list, profile: list, base_lv: int):
    """
        Plot function which analyzes user's record.

        :param music_map: a list of all available music records, each line of music_map should be like:
                          [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
                          all of them are strings, except vf is a float
        :param profile:   a list of [card_num, user_name, aka_name, ap_card, skill], all strings
        :param base_lv:   lowest level to analysis
        :return:          image stored as numpy array
        """

    def load_num(lv_int: int, refactor: float = False) -> tuple:
        lv_str = str(lv_int).zfill(2)
        __num_f = cv2.imread(img_archive + 'number/num_score_%s.png' % lv_str[0], cv2.IMREAD_UNCHANGED)
        __num_l = cv2.imread(img_archive + 'number/num_score_%s.png' % lv_str[1], cv2.IMREAD_UNCHANGED)
        if refactor:
            cv2.resize(__num_f, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
            cv2.resize(__num_l, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
        return __num_f, __num_l

    def statistic_pie(data_list: list, color_tuple: tuple, legend: tuple, size: tuple, l_col: int = 1) -> plt.figure:
        fig = plt.figure(figsize=size)
        __data_list = []
        __color_list = []

        if data_list[0]:
            wig = dict(width=0.4, edgecolor='w', lw=2)
            __data_list.append(data_list[0])
            __color_list.append(color_tuple[0])
            for index in range(1, len(data_list)):
                if data_list[index]:
                    __data_list.append(data_list[index])
                    __color_list.append(color_tuple[index])
            if len(__data_list) == 1:
                return None
            plt.pie(__data_list, radius=1, colors=__color_list, autopct='%.1f%%', pctdistance=0.8,
                    wedgeprops=wig, textprops={'fontsize': 15}, startangle=0, counterclock=False)
            plt.pie(__data_list[1:], radius=0.6, colors=__color_list[1:],
                    wedgeprops=wig, textprops={'fontsize': 15}, startangle=0, counterclock=False)
        else:
            for index in range(len(data_list)):
                if data_list[index]:
                    __data_list.append(data_list[index])
                    __color_list.append(color_tuple[index])
            wig = dict(width=0.6, edgecolor='w', lw=2)
            plt.pie(__data_list, radius=1, colors=__color_list, autopct='%.1f%%', pctdistance=0.75,
                    wedgeprops=wig, textprops={'fontsize': 14}, startangle=0, counterclock=False)

        patch = plt.pie(np.ones(len(color_tuple), dtype=int), radius=0, colors=color_tuple)[0]
        plt.legend(patch, legend, fontsize=15, loc=(0, -0.5), ncol=l_col)

        return fig

    def statistic_histogram(data_list: list, size: tuple, legend: list or tuple, color: tuple):
        fig, ax = plt.subplots(figsize=size)
        sns.histplot(data_list, palette=color, binwidth=2, legend=False, ax=ax, alpha=1)

        ax.spines['bottom'].set_color('w')
        ax.spines['bottom'].set_linewidth(2)
        ax.spines['top'].set_color('w')
        ax.spines['top'].set_linewidth(2)
        ax.spines['left'].set_color('w')
        ax.spines['left'].set_linewidth(2)
        ax.spines['right'].set_color('w')
        ax.spines['right'].set_linewidth(2)
        ax.tick_params(axis='x', colors='w', width='2')
        ax.tick_params(axis='y', colors='w', width='2')
        plt.xlim((900, 1000))
        plt.xticks(np.arange(900, 1001, 10), fontsize=13)
        plt.yticks(fontsize=13)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('')
        plt.ylabel('')
        plt.legend(legend, fontsize=14)

        return fig

    def statistic_joint(data_frame: pd.DataFrame, size: int, low_score: int, high_vf: float, low_vf: float):
        sns.set_style(rc={'xtick.color': 'w', 'ytick.color': 'w', 'axes.labelcolor': 'w'})
        sns.set_context("talk")
        x_lim_low = low_score // 100000 * 100000
        sns.jointplot(data=data_frame, hue='lv', x='score', y='vf', height=size, xlim=(x_lim_low, 10000000),
                      ylim=(low_vf - 0.2, high_vf + 0.2), alpha=0.9) \
            .set_axis_labels('SCORE', 'VOLFORCE')

    def statistic_violin(data_frame: pd.DataFrame, size: tuple):
        fig, ax = plt.subplots(figsize=size)
        sns.set_context("notebook")
        sns.violinplot(data=data_frame, x='lv', y='score', inner=None, color='.8')
        sns.stripplot(data=data_frame, x='lv', y='score')

        plt.ylabel('SCORE')
        plt.xlabel('LEVEL')
        plt.yticks([8700000, 9000000, 9300000, 9500000, 9700000, 9800000, 9900000, 10000000],
                   [870, 900, 930, 950, 970, 980, 990, 1000])

    card_num, user_name, aka_name, ap_card, skill = profile
    music_map_sort = music_map.copy()
    music_map_sort.sort(key=lambda x: x[10], reverse=True)

    # Get overall volforce
    vol_force = get_overall_vf(music_map_sort[0:50])
    log_write('Get overall volforce complete', file_name)

    # Check validity of ceil and floor
    if music_map_sort[0][0]:
        ceil_num = music_map_sort[0][-1] / 2
    else:
        ceil_num = 0.0
    if music_map_sort[49][0]:
        floor_num = music_map_sort[49][-1] / 2
    else:
        floor_num = 0.0

    # Get default level summary
    clear_index = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    grade_index = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 14, 9: 15, 10: 16}

    level_summary = np.zeros((21, 18), dtype=int)
    # 0-5  |  [NoRecord, TrackCrash, NormalClear, HardClear, UltimateChain, PerfectUltimateChain]
    #         [NO, CR, NC, HC, UC, PUC]
    # 6-16 |  [NO, D, C, B, A, A+, AA, AA+, AAA, AAA+, S]
    # 17   |  [sum]
    score_summary = [[[], [], [], [], [], []] for _ in range(21)]  # [[A+], [AA], [AA+], [AAA], [AAA+], [S]]
    violin_data = []
    for single_music in level_table:
        if not single_music[0]:
            continue
        nov, adv, exh, inf, mxm = int(single_music[7]), int(single_music[10]), int(single_music[13]), \
                                  int(single_music[16]), int(single_music[19])
        level_summary[nov][17] += 1
        level_summary[adv][17] += 1
        level_summary[exh][17] += 1
        level_summary[inf][17] += 1
        level_summary[mxm][17] += 1

    # Due to the "Automation Paradise", there are 2 ghost song in music_db.xml which should be eliminated.
    level_summary[7][17] -= 2
    level_summary[13][17] -= 2
    level_summary[16][17] -= 2
    level_summary[18][17] -= 2

    for record in music_map:
        if not record[0]:
            continue
        score, clear, grade, lv = int(record[3]), int(record[4]), int(record[5]), int(record[8])
        level_summary[lv][clear_index[clear]] += 1
        level_summary[lv][grade_index[grade]] += 1
        score_summary[lv][grade_index[grade] - 11].append(score // 10000)

        if lv >= base_lv and score > 8000000:
            violin_data.append([score, str(lv)])

    for single_level in level_summary:
        lighted = sum(single_level[1:6])
        graded = sum(single_level[7:17])
        single_level[0] = single_level[-1] - lighted
        single_level[6] = single_level[-1] - graded

    # Load images
    px_prologue, px_per_lv, px_epilogue = 450, 2300, 1800
    y_px = px_prologue + px_per_lv * (21 - base_lv) + px_epilogue
    bg_size = (y_px, 1080)
    bg = generate_hex_bg(bg_size)
    mark_list = load_marks(1.1)
    grade_list = load_grade(0.7)

    # Plot images about user profile
    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    # card_img = cv2.resize(card_img, dsize=None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, card_img, [100, 180])

    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_img = cv2.resize(skill_img, dsize=None, fx=0.51, fy=0.51, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, skill_img, [320, 180])

    name_bar_pos, name_bar_size = (220, 410), (4, 580)  # Bar between name field and vf field
    name_bar = simple_rectangle(name_bar_size, color_gray, bg.dtype)
    parabola_gradient(name_bar, -0.5, 1.08)
    png_superimpose(bg, name_bar, name_bar_pos, 0.6)

    vf_level = get_vf_property(vol_force, is_level=True)
    force_img = cv2.imread(img_archive + 'vf/em6_' + str(vf_level).zfill(2) + '_i_eab.png', cv2.IMREAD_UNCHANGED)
    force_img = cv2.resize(force_img, dsize=None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA)
    png_superimpose(bg, force_img, [220, 410])

    # Plot Summary for each level
    cen_box_size = (16, 840)
    cen_box_y = 22
    cen_box = simple_rectangle(cen_box_size, color_gray, bg.dtype)
    parabola_gradient(cen_box, -1.4, 1.6, 'x+')

    pilcrow_size = (16, 16)
    pilcrow = simple_rectangle(pilcrow_size, color_gray, bg.dtype)

    for lv_index in range(21 - base_lv):
        lv_cur = lv_index + base_lv
        y_cur = px_prologue + px_per_lv * lv_index
        y_seg = y_cur  # segment

        # Plot dividing line
        cen_box_pos = (y_seg + cen_box_y, (bg_size[1] - cen_box_size[1]) // 2)
        png_superimpose(bg, cen_box, cen_box_pos, 0.65)

        num_f, num_l = load_num(lv_cur)
        num_y = 0
        num_f_pos, num_l_pos = [num_y + y_seg, 140], [num_y + y_seg, 200]
        if lv_cur // 10 == 1:  # The number "1" is too thin to fit in
            num_l_pos[1] -= 10
        png_superimpose(bg, num_f, num_f_pos)
        png_superimpose(bg, num_l, num_l_pos)

        # Plot clear mark
        y_seg += 100

        pilcrow_y = 10
        pilcrow_pos = (pilcrow_y + y_seg, (bg_size[1] - cen_box_size[1]) // 2)
        png_superimpose(bg, pilcrow, pilcrow_pos, 0.65)

        clear_base = (70 + y_seg, 150)
        clear_precession = (110, 200)  # **_pre means precession, not "pxs pre **" XD
        grid_plot(bg, mark_list, clear_base, clear_precession, 1, 'x')

        clear_data = level_summary[lv_cur][:6]
        clear_pie_base = (-230, 375)
        clear_pie_pos = (clear_pie_base[0] + y_seg, clear_pie_base[1])
        clear_pie_size = (600 / 100, 1000 / 100)
        clear_pie = statistic_pie(clear_data, color_list, clear_legend, clear_pie_size)
        if clear_pie is not None:
            plot_matplotlib(bg, clear_pie_pos, local_dir)

        # Plot grade mark
        y_seg += 825

        pilcrow_y = 10
        pilcrow_pos = (pilcrow_y + y_seg, (bg_size[1] - cen_box_size[1]) // 2)
        png_superimpose(bg, pilcrow, pilcrow_pos, 0.65)
        grade_base, grade_pre = 140, 60

        grade_base = (70 + y_seg, 710)
        grade_precession = (110, 200)
        grid_plot(bg, grade_list[-6:], grade_base, grade_precession, 1, 'x')

        grade_data = level_summary[lv_cur][6:17]
        grade_pie_base = (-240, 85)
        grade_pie_pos = (grade_pie_base[0] + y_seg, grade_pie_base[1])
        grade_pie_size = (600 / 100, 1000 / 100)
        grade_pie = statistic_pie(grade_data, grade_color_table, grade_legend, grade_pie_size, l_col=2)
        if grade_pie is not None:
            plot_matplotlib(bg, grade_pie_pos, local_dir)

        # Plot histogram
        y_seg += 825

        score_size = (900 / 100, 500 / 100)
        score_data = score_summary[lv_cur]
        score_pos = (-30 + y_seg, 100)
        score_legend = ['S', 'AAA+', 'AAA', 'AA+', 'AA', 'A+']
        score_his = statistic_histogram(score_data, score_size, score_legend, grade_color_table[-6:])
        if score_his is not None:
            plot_matplotlib(bg, score_pos, local_dir)

    # Plot epilogue
    y_cur = y_px - px_epilogue
    pilcrow_pos = (y_cur + 20, (bg_size[1] - cen_box_size[1]) // 2)
    png_superimpose(bg, pilcrow, pilcrow_pos, 0.65)

    # Plot joint graph
    y_cur += 100

    joint_data = []
    joint_size = 800 // 100
    low_score = 10000000
    joint_pos = (0 + y_cur, (bg_size[1] - joint_size * 100) // 2)
    for music_record in music_map_sort[:100]:
        if music_record[0]:
            score, lv, vf = int(music_record[3]), str(music_record[8]), music_record[10]
            joint_data.append((score, vf / 2, lv))
            if score < low_score:
                low_score = score
    high_vf, low_vf = joint_data[0][1], joint_data[-1][1]
    joint_df = pd.DataFrame(joint_data, columns=['score', 'vf', 'lv'])
    statistic_joint(joint_df, joint_size, low_score, high_vf, low_vf)
    plot_matplotlib(bg, joint_pos, local_dir)

    # Plot violin_graph
    y_cur += 850

    pilcrow_pos = (y_cur + 20, (bg_size[1] - cen_box_size[1]) // 2)
    png_superimpose(bg, pilcrow, pilcrow_pos, 0.65)

    y_cur += 50
    violin_size = (900 // 100, 700 // 100)
    violin_pos = (0 + y_cur, (bg_size[1] - violin_size[0] * 100) // 2)
    violin_df = pd.DataFrame(violin_data, columns=['score', 'lv'])
    statistic_violin(violin_df, violin_size)
    plot_matplotlib(bg, violin_pos, local_dir)

    # Initialize fonts
    user_font = ImageFont.truetype(font_DFHS, 55, encoding='utf-8', index=0)
    id_font = ImageFont.truetype(font_DFHS, 28, encoding='utf-8', index=0)
    vol_font = ImageFont.truetype(font_DFHS, 30, encoding='utf-8', index=0)
    vol_num_font = ImageFont.truetype(font_unipace, 29, encoding='utf-8')
    ceil_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
    ceil_num_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')

    subtitle_font = ImageFont.truetype(font_DFHS, 34, encoding='utf-8')
    sta_b_font = ImageFont.truetype(font_unipace, 33, encoding='utf-8')
    sta_s_font = ImageFont.truetype(font_unipace, 16, encoding='utf-8')
    author_font = ImageFont.truetype(font_DFHS, 24, encoding='utf-8')

    # Stipulate absolute and relative position
    abs_user, abs_id, abs_vol, abs_vol_num, abs_ceil, abs_floor, abs_ceil_num, abs_floor_num = \
        (420, 106), (420, 170), (570, 255), (780, 254), (689, 305), (659, 335), (780, 305), (780, 335)

    small_sta_pre = (0, 40)

    # Plot characters
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(bg)
    pen = ImageDraw.Draw(pil_img)

    # Plot profile characters
    pen.text(abs_user, user_name, color_white, font=user_font)
    pen.text(abs_id, 'ID  ' + card_num, color_white, font=id_font)
    pen.text(abs_vol, 'VOLFORCE', color_white, font=vol_font)
    pen.text(abs_vol_num, ('%.3f' % vol_force), get_vf_property(vol_force), font=vol_num_font)
    pen.text(abs_ceil, 'CEIL', color_white, font=ceil_font)
    pen.text(abs_floor, 'FLOOR', color_white, font=ceil_font)
    pen.text(abs_ceil_num, ('%.3f' % ceil_num), get_vf_property(ceil_num), font=ceil_num_font)
    pen.text(abs_floor_num, ('%.3f' % floor_num), get_vf_property(floor_num), font=ceil_num_font)

    # Plot characters for each level
    for lv_index in range(21 - base_lv):
        lv_cur = lv_index + base_lv
        y_cur = px_prologue + px_per_lv * lv_index
        lv_sum = level_summary[lv_cur][-1]
        y_seg = y_cur

        # Plot clear mark data
        y_seg += 100
        pos_grade_t, pos_grade_sta, pos_grade_foot = (160, 0), (275, 83), (280, 710)

        grade_title = (pos_grade_t[0], pos_grade_t[1] + y_seg)
        pen.text(grade_title, 'Clear Marks', color_l_gray, font=subtitle_font)

        clear_data = level_summary[lv_cur][:6]
        clear_data_small = []
        clear_cur, clear_color = 0, []
        clear_base = (pos_grade_sta[0], pos_grade_sta[1] + y_seg)
        clear_precession = (220, 110)  # It should keep in line with the image's, in a reversed way

        for data in clear_data[::-1]:
            clear_cur += data
            clear_data_small.append('(%d)' % clear_cur)
            if clear_cur == lv_sum:
                clear_color.append(color_gold)
            else:
                clear_color.append(color_l_gray)
        clear_color.reverse()
        clear_data_small.reverse()
        clear_data_small[0] = clear_data_small[1] = '-'
        clear_color[0] = clear_color[1] = color_l_gray
        if clear_data[0] or clear_data[1]:
            clear_color = [color_l_gray] * 6

        grid_text(clear_data, clear_color, clear_base, clear_precession, 1, pen, sta_b_font)
        clear_base_small = (clear_base[0] + small_sta_pre[0], clear_base[1] + small_sta_pre[1])
        grid_text(clear_data_small, clear_color, clear_base_small, clear_precession, 1, pen, sta_s_font)

        clear_foot_base = (pos_grade_foot[0], pos_grade_foot[1] + y_seg)
        pen.text(clear_foot_base, '/%s' % lv_sum, color_l_gray, font=sta_b_font)

        # Plot grade mark data
        y_seg += 825
        pos_grade_t, pos_grade_sta, pos_grade_foot = (160, 0), (830, 83), (835, 710)

        grade_title = (pos_grade_t[0], pos_grade_t[1] + y_seg)
        pen.text(grade_title, 'Grade Marks', color_l_gray, font=subtitle_font)

        grade_data = level_summary[lv_cur][6:17]
        grade_data_small = []
        grade_cur, grade_color = 0, []
        grade_base = (pos_grade_sta[0], pos_grade_sta[1] + y_seg)
        grade_precession = (220, 110)

        for data in grade_data[::-1]:
            grade_cur += data
            grade_data_small.append('(%d)' % grade_cur)
            if grade_cur == lv_sum:
                grade_color.append(color_gold)
            else:
                grade_color.append(color_l_gray)
        grade_color.reverse()
        grade_data_small.reverse()
        grade_data_small[0] = grade_data_small[1] = '-'
        if grade_data[0] or grade_data[1]:
            grade_color = [color_l_gray] * 6

        grade_data = grade_data[-6:]
        grade_data_small = grade_data_small[-6:]
        grade_color = grade_color[-6:]

        grid_text(grade_data, grade_color, grade_base, grade_precession, 1, pen, sta_b_font)
        grade_base_small = (grade_base[0] + small_sta_pre[0], grade_base[1] + small_sta_pre[1])
        grid_text(grade_data_small, grade_color, grade_base_small, grade_precession, 1, pen, sta_s_font)

        grade_foot_base = (pos_grade_foot[0], pos_grade_foot[1] + y_seg)
        pen.text(grade_foot_base, '/%s' % lv_sum, color_l_gray, font=sta_b_font)

    # Plot epilogue characters
    y_cur = y_px - px_epilogue
    pos_epi_t = (160, 10)
    epi_title = (pos_epi_t[0], pos_epi_t[1] + y_cur)
    pen.text(epi_title, 'Best 100 Joint Graph', color_l_gray, font=subtitle_font)

    y_cur += 100
    y_cur += 850
    epi_title = (pos_epi_t[0], pos_epi_t[1] + y_cur)
    pen.text(epi_title, 'Chosen Level [%d~20] Violin Graph' % base_lv, color_l_gray, font=subtitle_font)

    # Plot author
    pos_author = (bg_size[1] // 2 - 208, y_px - 37)
    pen.text(pos_author, 'Ploted by Saccharomyces cerevisiae', color_gray, font=author_font)

    bg = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    # cv2.imshow('test', bg)
    # cv2.waitKey(0)

    cv2.imwrite('%s/%s_summary.png' % (output, user_name), bg, params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

    # It seems an image over 10k px is too big to Tencent
    # CNM, Tencent
    cv2.imwrite('%s/%s_summary.jpg' % (output, user_name), bg, params=[cv2.IMWRITE_JPEG_QUALITY, 93])


def plot_summary(music_map: list, profile: list, lv_base: int):
    """
         Plot function which analyzes user's record.
         :param music_map: a list of all available music records, each line of music_map should be like:
                           [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
                           all of them are strings, except vf is a float
         :param profile:   a list of [card_num, user_name, aka_name, ap_card, skill], all strings
         :param lv_base:   lowest level to analysis
    """

    def load_num(lv_int: int, refactor: float = False) -> tuple:
        lv_str = str(lv_int).zfill(2)
        __num_f = cv2.imread(img_archive + 'number/num_score_%s.png' % lv_str[0], cv2.IMREAD_UNCHANGED)
        __num_l = cv2.imread(img_archive + 'number/num_score_%s.png' % lv_str[1], cv2.IMREAD_UNCHANGED)
        if refactor:
            cv2.resize(__num_f, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
            cv2.resize(__num_l, dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
        return __num_f, __num_l

    """
    Read and initialize data
    """
    card_num, user_name, aka_name, ap_card, skill = profile  # get profile data
    music_map_sort = music_map.copy()
    music_map_sort.sort(key=lambda x: x[10], reverse=True)  # make a sorted map duplicate

    vol_force = get_overall_vf(music_map_sort[0:50])  # Get overall volforce
    log_write('Get overall volforce complete', file_name)

    if music_map_sort[0][0]:  # validity check for floor and ceil
        ceil_num = music_map_sort[0][-1] / 2
    else:
        ceil_num = 0.0
    if music_map_sort[49][0]:
        floor_num = music_map_sort[49][-1] / 2
    else:
        floor_num = 0.0

    level_summary = np.zeros((21, 18), dtype=int)  # Get default level summary
    clear_index = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    grade_index = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 14, 9: 15, 10: 16}
    # 0-5  |  [NoRecord, TrackCrash, NormalClear, HardClear, UltimateChain, PerfectUltimateChain]
    #         [NO, CR, NC, HC, UC, PUC]
    # 6-16 |  [NO, D, C, B, A, A+, AA, AA+, AAA, AAA+, S]
    # 17   |  [sum]
    for single_music in level_table:  # Calculating the sum of eachlevel
        if not single_music[0]:
            continue
        nov, adv, exh, inf, mxm = int(single_music[7]), int(single_music[10]), int(single_music[13]), \
                                  int(single_music[16]), int(single_music[19])
        level_summary[nov][17] += 1
        level_summary[adv][17] += 1
        level_summary[exh][17] += 1
        level_summary[inf][17] += 1
        level_summary[mxm][17] += 1

    # Due to the "Automation Paradise", there are 2 ghost song in music_db.xml which should be eliminated.
    level_summary[7][17] -= 2
    level_summary[13][17] -= 2
    level_summary[16][17] -= 2
    level_summary[18][17] -= 2

    # Generate data frame for histogram, violin plot
    score_list = []  # Each line should be [score: int, grade: int, lv: str, is_hist: bool, is_vio: bool]
    for record in music_map:
        if not record[0]:
            continue
        score, clear, grade, lv = int(record[3]), int(record[4]), int(record[5]), int(record[8])
        if clear == 6:  # Saved = Track Crash
            level_summary[lv][1] += 1
        else:
            level_summary[lv][clear_index[clear]] += 1
        level_summary[lv][grade_index[grade]] += 1
        score_list.append([score, grade, str(lv), (score > 9000000), (score > 8000000)])
    score_df = pd.DataFrame(score_list, columns=['score', 'grade', 'lv', 'is_hist', 'is_vio'])

    # Generate data frame for joint plot
    vf_list, vf_size, low_score = [], 100, 10000000  # Just [score: int, vf: float, lv: str]
    for record in music_map_sort[:vf_size]:
        if record[0]:
            score, lv, vf = int(record[3]), str(record[8]), record[10]
            vf_list.append((score, vf / 2, lv))
            low_score = min(low_score, score)
    high_vf, low_vf = vf_list[0][1], vf_list[-1][1]
    vf_df = pd.DataFrame(vf_list, columns=['score', 'vf', 'lv'])

    """
    Generate background, text layer and load image ingredients
    """
    px_prologue, px_chapters, px_epilogue = 450, 1800, 1500
    y_px = px_prologue + px_chapters * (21 - lv_base) + px_epilogue
    y_px = 2250  # FIXME: temp variable
    bg = generate_hex_bg((y_px, 1080))

    blank_layer = np.zeros((y_px, 1080, 3), dtype=bg.dtype)  # generate text layer
    text_layer = Image.fromarray(blank_layer)
    text_layer.putalpha(1)
    pen = ImageDraw.Draw(text_layer)

    clear_ref, grade_ref, box_ref = 1, 0.45, 1.09
    clear_list = load_marks()
    grade_list = load_grade(grade_ref)
    clear_list[0] = cv2.resize(clear_list[0], dsize=None, fx=0.7, fy=0.7, interpolation=cv2.INTER_AREA)

    preface = Anchor(bg, 'preface')  # supreme anchor
    prologue = Anchor(bg, 'prologue', free=(0, 0), father=preface)
    chapters = Anchor(bg, 'chapters', free=(px_prologue, 0), father=preface)
    chapters.creat_grid(grid=(20 - lv_base, 0), precession=(px_chapters, 0))
    epilogue = Anchor(bg, 'epilogue', free=(y_px - px_epilogue, 0), father=preface)

    """
    Prologue: Use profile
    """
    # Profile field includes card field and name field
    profile_field = Anchor(bg, 'card field', free=(60, 100), father=prologue)
    profile_size = (340, 800)

    """
    # Profile background
    pbg_frame = simple_rectangle(profile_size, color_white, bg.dtype, 6)  # pbg = profile background
    parabola_gradient(pbg_frame, -1, 1, 'x+')
    pbg_frame_anc = AnchorImage(bg, 'profile bg frame', pbg_frame, father=profile_field)

    pbg_belt = simple_rectangle((800, 40), color_white, bg.dtype)
    parabola_gradient(pbg_belt, -1, 1, 'x+')
    pbg_belt1_anc = AnchorImage(bg, 'profile bg belt upper', pbg_belt, father=profile_field)
    pbg_belt2_anc = AnchorImage(bg, 'profile bg belt lower', pbg_belt, father=profile_field,
                                free=(0, profile_size[1] - pbg_belt.shape[0]))

    pbg_neon = simple_rectangle((80, profile_size[1]), (109,46,186), bg.dtype)
    parabola_gradient(pbg_neon, -2, 1, 'x+')
    pbg_neon_anc = AnchorImage(bg, 'profile skill neon', pbg_neon, father=profile_field)

    pbg_neon_anc.plot(transparency=0.7)
    pbg_belt1_anc.plot(transparency=0.5)
    pbg_belt2_anc.plot(transparency=0.5)

    pbg_frame_anc.plot()
    """

    # Card field contains two images, namely appeal card and skill
    card_field = Anchor(bg, 'card field', free=(40, 80), father=profile_field)

    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    card_anc = AnchorImage(bg, 'appeal card', card_img, (0, 0), father=card_field)

    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_ratio = card_img.shape[1] / skill_img.shape[1]
    skill_img = cv2.resize(skill_img, dsize=None, fx=skill_ratio, fy=skill_ratio, interpolation=cv2.INTER_AREA)
    skill_anc = AnchorImage(bg, 'skill', skill_img, (220, 0), father=card_field)

    card_anc.plot()
    skill_anc.plot()

    data_field = Anchor(bg, 'profile data field', free=(40, 300), father=profile_field)

    name_bar_size = (4, 580)
    name_bar = simple_rectangle(name_bar_size, color_gray, bg.dtype)
    name_bar_anc = AnchorImage(bg, 'name bar', name_bar, free=(120, 10), father=data_field)
    parabola_gradient(name_bar, -0.65, 1.14)
    name_bar_anc.plot()

    vf_level = get_vf_property(vol_force, is_level=True)
    force_img = cv2.imread(img_archive + 'vf/em6_' + str(vf_level).zfill(2) + '_i_eab.png', cv2.IMREAD_UNCHANGED)
    force_img = cv2.resize(force_img, dsize=None, fx=0.35, fy=0.35, interpolation=cv2.INTER_AREA)
    force_anc = AnchorImage(bg, 'volforce', force_img, free=(120, 10), father=data_field)

    name_field = Anchor(bg, 'name field', free=(6, 20), father=data_field)

    user_font = ImageFont.truetype(font_DFHS, 55, encoding='utf-8', index=0)
    user_anc = AnchorText(bg, 'user name', user_name, pen, user_font, free=(0, 0), father=name_field)
    id_font = ImageFont.truetype(font_DFHS, 30, encoding='utf-8', index=0)
    id_anc = AnchorText(bg, 'user id', 'ID  ' + card_num, pen, id_font, free=(65, 0), father=name_field)

    vf_field = Anchor(bg, 'vf field', free=(155, 170), father=data_field)

    vol_font = ImageFont.truetype(font_DFHS, 30, encoding='utf-8', index=0)
    vol_anc = AnchorText(bg, 'vf text', 'VOLFORCE', pen, vol_font, free=(0, 0), father=vf_field)
    vol_num_font = ImageFont.truetype(font_unipace, 29, encoding='utf-8')
    vol_num_anc = AnchorText(bg, 'vf num', ('%.3f' % vol_force), pen, vol_num_font, free=(-1, 210), father=vf_field)

    ceil_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
    ceil_anc = AnchorText(bg, 'ceil text', 'CEIL', pen, ceil_font, free=(50, 119), father=vf_field)
    floor_anc = AnchorText(bg, 'floor text', 'FLOOR', pen, ceil_font, free=(80, 89), father=vf_field)
    ceil_num_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')
    ceil_num_anc = AnchorText(bg, 'ceil num', ('%.3f' % ceil_num), pen, ceil_num_font, free=(50, 210), father=vf_field)
    floor_num_anc = AnchorText(bg, 'floor num', ('%.3f' % floor_num), pen, ceil_num_font, (80, 210), father=vf_field)

    force_anc.plot()

    user_anc.plot(color_white)
    id_anc.plot(color_white)
    vol_anc.plot(color_white)
    vol_num_anc.plot(get_vf_property(vol_force))
    ceil_anc.plot(color_white)
    floor_anc.plot(color_white)
    ceil_num_anc.plot(get_vf_property(ceil_num))
    floor_num_anc.plot(get_vf_property(floor_num))

    """
    Chapter 1: Data initialization
    """
    # Initialize Level-title box, pilcrow, set of clear mark and set of grade mark
    cen_box_size = (16, 840)
    cen_box = simple_rectangle(cen_box_size, color_gray, bg.dtype)
    parabola_gradient(cen_box, -1.4, 1.6, 'x+')
    cen_box_anc = AnchorImage(bg, 'title box', cen_box, free=(22, -20))

    subtitle_font = ImageFont.truetype(font_DFHS, 34, encoding='utf-8')
    sta_b_font = ImageFont.truetype(font_unipace, 36, encoding='utf-8')
    sta_s_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')

    pilcrow_size = (16, 16)
    pilcrow = simple_rectangle(pilcrow_size, color_white, bg.dtype)
    pilcrow_anc = AnchorImage(bg, 'pilcrow', pilcrow, free=(10, -20))

    icon_bg = cv2.imread(img_archive + 'grade/box_medal.png', cv2.IMREAD_UNCHANGED)
    icon_bg = cv2.resize(icon_bg, dsize=None, fx=box_ref, fy=box_ref, interpolation=cv2.INTER_AREA)
    icon_glow = outer_glow(icon_bg, color_l_blue, 25)
    glow_anc = AnchorImage(bg, 'icon glow', icon_glow, free=(-icon_bg.shape[0], -icon_bg.shape[1]))

    sqrt_3, hex_y = np.sqrt(3), 36  # arrange icons in hex
    clear_grid = Anchor(bg, 'clear grid', free=(85, 40))
    clear_grid.creat_grid((5, 5), (hex_y, int(hex_y * sqrt_3)))
    clear_content = [None, None, None, None, None, None]
    clear_icon = [None, None, None, None, None, None]
    clear_text_b = [None, None, None, None, None, None]
    clear_text_s = [None, None, None, None, None, None]
    for index in range(6):
        __clear_bg = icon_bg.copy()
        clear_content[index] = AnchorImage(bg, 'clear img %d' % index, __clear_bg, father=clear_grid)
        clear_content[index].set_grid((index, index % 2))
        clear_icon[index] = AnchorImage(__clear_bg, 'clear icon %d' % index, clear_list[index])
        clear_icon[index].plot_center(offset=(1, 1))
        clear_text_b[index] = AnchorText(bg, 'clear text big %d' % index, '', pen, sta_b_font, (10, -100), clear_grid)
        clear_text_b[index].set_grid((index, index % 2 * 5))
        clear_text_s[index] = AnchorText(bg, 'clear text small %d' % index, '', pen, sta_s_font, (50, -100), clear_grid)
        clear_text_s[index].set_grid((index, index % 2 * 5))

    grade_grid = Anchor(bg, 'grade grid', free=(85, 40))
    grade_grid.creat_grid((5, 5), (hex_y, int(hex_y * sqrt_3)))
    grade_content = [None, None, None, None, None, None]
    grade_icon = [None, None, None, None, None, None]
    grade_text_b = [None, None, None, None, None, None]
    grade_text_s = [None, None, None, None, None, None]
    for index in range(6):
        __grade_bg = icon_bg.copy()
        grade_content[index] = AnchorImage(bg, 'grade bg %d' % index, __grade_bg, father=grade_grid)
        grade_content[index].set_grid((index, (1 - (index % 2))))
        grade_icon[index] = AnchorImage(__grade_bg, 'grade icon %d' % index, grade_list[index - 6])
        grade_icon[index].plot_center()
        grade_text_b[index] = AnchorText(bg, 'grade text big %d' % index, '', pen, sta_b_font, (10, -100), grade_grid)
        grade_text_b[index].set_grid((index, (1 - (index % 2)) * 5))
        grade_text_s[index] = AnchorText(bg, 'grade text small %d' % index, '', pen, sta_s_font, (50, -100), grade_grid)
        grade_text_s[index].set_grid((index, (1 - (index % 2)) * 5))

    # Plot them by level
    for lv_index in range(21 - lv_base):
        """
        Chapter 2: Topmost level box
        """
        lv_cur = lv_index + lv_base
        lv_sum = level_summary[lv_cur][-1]
        lv_field = Anchor(bg, 'level field', father=chapters)
        lv_field.set_grid((lv_index, 0))

        num_field = Anchor(bg, 'numbers', father=lv_field, free=(0, 140))

        num_f, num_l = load_num(lv_cur)
        num_f_anc = AnchorImage(bg, 'num former', img=num_f, father=num_field)
        num_precession = 60 - (lv_cur // 10 == 1) * 10
        num_l_anc = AnchorImage(bg, 'num latter', img=num_l, father=num_field, free=(0, num_precession))

        cen_box_anc.set_father(num_field)

        cen_box_anc.plot()
        num_f_anc.plot()
        num_l_anc.plot()

        """
        Chapter 3: Clear marks
        """
        clear_field = Anchor(bg, 'clear field', father=lv_field, free=(100, 140))

        pilcrow_anc.set_father(clear_field)
        clear_title_anc = AnchorText(bg, 'clear subtitle', 'Clear Marks', pen, subtitle_font, (0, 20), clear_field)
        clear_grid.set_father(clear_field)

        # Clear data and texts
        clear_data = level_summary[lv_cur][:6]
        clear_data_small = []
        clear_cur, clear_color = 0, []

        for data in clear_data[::-1]:
            clear_cur += data
            clear_data_small.append('(%d)' % clear_cur)
            if clear_cur == lv_sum:
                clear_color.append(color_gold)
            else:
                clear_color.append(color_l_gray)
        clear_color.reverse()
        clear_data_small.reverse()
        clear_data_small[0] = clear_data_small[1] = '-'
        clear_color[0] = clear_color[1] = color_l_gray
        if clear_data[0] or clear_data[1]:
            clear_color = [color_l_gray] * 6

        pilcrow_anc.plot()
        clear_title_anc.plot(color_l_gray)
        for index in range(6):
            clear_content[index].update_pos()
            glow_anc.set_father(clear_content[index])
            glow_anc.plot()
        for index in range(6):
            clear_content[index].plot()
            clear_text_b[index].text = str(clear_data[index])
            clear_text_b[index].plot(clear_color[index])
            clear_text_s[index].text = clear_data_small[index]
            clear_text_s[index].plot(clear_color[index])

        """
        Chapter 4: Grade Marks
        """
        grade_field = Anchor(bg, 'grade_field', father=lv_field, free=(100, 580))

        pilcrow_anc.set_father(grade_field)
        pilcrow_anc.set_free((10, -20))

        grade_title_anc = AnchorText(bg, 'grade subtitle', 'Grade Marks', pen, subtitle_font, (0, 20), grade_field)
        grade_grid.set_father(grade_field)

        # Grade data and texts
        grade_data = level_summary[lv_cur][6:17]
        grade_data_small = []
        grade_cur, grade_color = 0, []

        for data in grade_data[::-1]:
            grade_cur += data
            grade_data_small.append('(%d)' % grade_cur)
            if grade_cur == lv_sum:
                grade_color.append(color_gold)
            else:
                grade_color.append(color_l_gray)
        grade_color.reverse()
        grade_data_small.reverse()
        grade_data_small[0] = grade_data_small[1] = '-'
        if grade_data[0] or grade_data[1]:
            grade_color = [color_l_gray] * 6

        grade_data = grade_data[-6:]
        grade_data_small = grade_data_small[-6:]
        grade_color = grade_color[-6:]

        pilcrow_anc.plot()
        grade_title_anc.plot(color_l_gray)
        for index in range(6):
            grade_content[index].update_pos()
            glow_anc.set_father(grade_content[index])
            glow_anc.plot()
        for index in range(6):
            grade_content[index].plot()
            grade_text_b[index].text = str(grade_data[index])
            grade_text_b[index].plot(grade_color[index])
            grade_text_s[index].text = grade_data_small[index]
            grade_text_s[index].plot(grade_color[index])

        """
        Chapter 5: Pie Plot
        """
        pie_field = Anchor(bg, 'pie for two', (500, 0), father=lv_field)
        pie_px = (600, 1000)

        """
        Chapter 6: Histogram
        """
        hist_anc = Anchor(bg, 'histogram', (1000, 0), father=lv_field)
        break

    """
    Epilogue: Joint plot and violin plot
    """

    text_layer = np.array(text_layer)
    png_superimpose(bg, text_layer)

    cv2.imwrite('%s/%s_summary_temp.png' % (output, user_name), bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])
