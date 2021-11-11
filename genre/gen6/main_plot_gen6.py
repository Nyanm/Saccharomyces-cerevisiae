from .tools_plot_gen6 import *

img_archive = local_dir + '/img_archive/gen6/'
if not path.exists(img_archive):
    input(r'Image archive is missing, please check your file directory.')
    sys.exit(1)

# Fonts
font_DFHS = img_archive + 'font/DFHSMaruGothic-W4-reform.ttc'
font_unipace = img_archive + 'font/unispace bd.ttf'
font_round = img_archive + 'font/RoundedMplus1c-Black.ttf'

# Quick color table
color_white = (245, 245, 245)
color_black = (61, 61, 61)
color_gray = (154, 154, 154)
color_l_gray = (210, 210, 210)
color_d_gray = (122, 122, 122)
color_gold = (246, 222, 128)
color_l_blue = (147, 255, 254)
color_d_blue = (0, 62, 102)
color_yellow = (239, 176, 74)

# Definitive field for some dictionary(or they work as tuple)
clear_img = {'1': 'crash', '2': 'comp', '3': 'comp_ex', '4': 'uc', '5': 'puc'}
clear_table = {'1': 'FAILED', '2': 'NC', '3': 'HC', '4': 'UC', '5': 'PUC'}
clear_palette = ('#FFFFFF', '#32936F', '#69A297', '#A5668B', '#E83F6F', '#FFBF00')
clear_legend = ('N/A', 'CRASH', 'NC', 'HC', 'UC', 'PUC')

grade_img = {'1': 'd', '2': 'c', '3': 'b', '4': 'a', '5': 'a_plus', '6': 'aa', '7': 'aa_plus', '8': 'aaa',
             '9': 'aaa_plus', '10': 's'}
grade_table = {'1': 'D', '2': 'C', '3': 'B', '4': 'A', '5': 'A+',
               '6': 'AA', '7': 'AA+', '8': 'AAA', '9': 'AAA+', '10': 'S'}
grade_palette = ('#FFFFFF', '#CFD2CD', '#A6A2A2', '#847577',
                 '#66C9A3', '#32936F', '#D296B9', '#A5668B', '#E36E94', '#E83F6F', '#FFBF00',)
grade_legend = ('N/A', 'D', 'C', 'B', 'A', 'A+', 'AA', 'AA+', 'AAA', 'AAA+', 'S')

level_palette = ('#F7FFF7', '#073B4C', '#118AB2', '#06D6A0', '#FFD166', '#EF476F')

# Set up img_archive guidance
gen6_archive = {'version': '6',

                'ifs_list': (),
                'grade':''}


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


def get_jacket(mid: str, m_type: str, size: str = False) -> str:
    mid = mid.zfill(4)
    for song_folder in listdir(song_folders):
        if song_folder.startswith(mid):
            song_path = ('%s/%s/' % (song_folders, song_folder))
            m_index = int(m_type) + 1
            while m_index:
                if path.exists('%sjk_%s_%d.png' % (song_path, mid, m_index)):
                    if size:
                        return '%sjk_%s_%d_%s.png' % (song_path, mid, m_index, size)
                    return '%sjk_%s_%d.png' % (song_path, mid, m_index)
                m_index -= 1
            if size:
                return game_dir + '/data/graphics/jk_dummy_%s.png' % size
            else:
                return game_dir + '/data/graphics/jk_dummy_s.png'


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


def load_clear(refactor: float or int) -> list:
    clear_no = cv2.imread(img_archive + 'mark/mark_no.png', cv2.IMREAD_UNCHANGED)
    clear_cr = cv2.imread(img_archive + 'mark/mark_crash.png', cv2.IMREAD_UNCHANGED)
    clear_nc = cv2.imread(img_archive + 'mark/mark_comp.png', cv2.IMREAD_UNCHANGED)
    clear_hc = cv2.imread(img_archive + 'mark/mark_comp_ex.png', cv2.IMREAD_UNCHANGED)
    clear_uc = cv2.imread(img_archive + 'mark/mark_uc.png', cv2.IMREAD_UNCHANGED)
    clear_puc = cv2.imread(img_archive + 'mark/mark_puc.png', cv2.IMREAD_UNCHANGED)

    clear_list = [clear_no, clear_cr, clear_nc, clear_hc, clear_uc, clear_puc]
    if refactor:
        for index in range(6):
            if clear_list[index] is not None:
                clear_list[index] = \
                    cv2.resize(clear_list[index], dsize=None, fx=refactor, fy=refactor, interpolation=cv2.INTER_AREA)
    return clear_list


def load_grade(refactor: float or int) -> list:
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


def load_level(refactor: float or int) -> list:
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


def load_skill(card_img: np.array, skill: str) -> np.array:
    skill_img = cv2.imread(img_archive + 'skill/skill_' + skill.zfill(2) + '.png', cv2.IMREAD_UNCHANGED)
    skill_ratio = card_img.shape[1] / skill_img.shape[1]
    skill_img = cv2.resize(skill_img, dsize=None, fx=skill_ratio, fy=skill_ratio, interpolation=cv2.INTER_AREA)
    return skill_img


def load_frame() -> tuple:
    top_left = cv2.imread(img_archive + 'frame/top_left.png', cv2.IMREAD_UNCHANGED)
    top_right = cv2.imread(img_archive + 'frame/top_right.png', cv2.IMREAD_UNCHANGED)
    btm_left = cv2.imread(img_archive + 'frame/btm_left.png', cv2.IMREAD_UNCHANGED)
    btm_right = cv2.imread(img_archive + 'frame/btm_right.png', cv2.IMREAD_UNCHANGED)

    side_top = cv2.imread(img_archive + 'frame/top_orange.png', cv2.IMREAD_UNCHANGED)
    side_right = side_left = cv2.imread(img_archive + 'frame/bar.png', cv2.IMREAD_UNCHANGED)
    side_bottom = cv2.imread(img_archive + 'frame/btm_orange.png', cv2.IMREAD_UNCHANGED)
    return [top_left, top_right, btm_left, btm_right], [side_top, side_right, side_bottom, side_left]


def load_bar(name: str, is_bg: bool = False) -> list:
    left = cv2.imread(img_archive + 'bar/%s_left.png' % name, cv2.IMREAD_UNCHANGED)
    bar = cv2.imread(img_archive + 'bar/%s_bar.png' % name, cv2.IMREAD_UNCHANGED)
    right = cv2.imread(img_archive + 'bar/%s_right.png' % name, cv2.IMREAD_UNCHANGED)
    if is_bg:
        bg = cv2.imread(img_archive + 'bar/%s_bg.png' % name, cv2.IMREAD_UNCHANGED)
    else:
        bg = None
    return [left, bar, right, bg]


def generate_hex_bg(size: tuple, par_a: float = -0.55, par_c: float = 1.1):
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
    bg = add_alpha(bg)

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
    jk = cv2.imread(jk_path, cv2.IMREAD_UNCHANGED)
    jk = add_alpha(jk)
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
    :param profile:   a list of [user_name, aka_name, ap_card, skill], all strings
    :return:          image stored as numpy array
    """

    """
    Read and initialize data
    """
    # Unpack profile data & sort music records
    user_name, aka_name, ap_card, skill = profile
    music_map.sort(key=lambda x: x[10], reverse=True)
    music_b50 = music_map[:50]
    vol_force = get_overall_vf(music_b50)  # Get overall volforce

    # validity check for floor and ceil
    if music_b50[0][0]:
        ceil_num = music_b50[0][-1] / 2
    else:
        ceil_num = 0.0
    if music_b50[49][0]:
        floor_num = music_b50[49][-1] / 2
    else:
        floor_num = 0.0

    """
    Generate background, text layer and load image ingredients
    """
    # Stipulate the size of the background & generate
    px_prologue, px_chapters, px_epilogue = 350, 144, 70
    y_px, x_px = px_prologue + px_chapters * 25 + px_epilogue, 1280
    bg = generate_hex_bg((y_px, x_px))

    # Init text layer
    blank_layer = np.ones((y_px, x_px, 3), dtype=np.uint8) * 154  # Makeshift
    text_layer = Image.fromarray(blank_layer)
    text_layer.putalpha(1)
    pen = ImageDraw.Draw(text_layer)

    # Load image ingredients
    level_ref, clear_ref, grade_ref = 0, 0.58, 0.42
    level_list, clear_list, grade_list = load_level(level_ref), load_clear(clear_ref), load_grade(grade_ref)
    box = cv2.imread(img_archive + 'bg/box_semi.png', cv2.IMREAD_UNCHANGED)
    box_y, box_x, chn = box.shape

    # Genesis
    preface = Anchor(bg, 'preface')  # supreme anchor
    prologue = Anchor(bg, 'prologue', free=(0, 0), father=preface)
    chapters = Anchor(bg, 'chapter', free=(px_prologue, 0), father=preface)

    cell_gap = 20  # Cell gap defines who far between two adjacent boxes, both x axis and y axis
    cell_margin = (x_px - 2 * (box_x + cell_gap)) // 2
    cells = Anchor(bg, 'cells', free=(0, cell_margin), father=chapters)
    cells.creat_grid((24, 1), (px_chapters, box_x + cell_gap))

    epilogue = Anchor(bg, 'epilogue', free=(y_px - px_epilogue, 0), father=preface)

    """
    Prologue: Use profile
    """
    # Logo, relatively independent
    logo = cv2.imread(img_archive + '/version/logo.png', cv2.IMREAD_UNCHANGED)
    logo = cv2.resize(logo, dsize=None, fx=0.4, fy=0.4, interpolation=cv2.INTER_AREA)
    logo_anc = AnchorImage(bg, 'logo', logo, free=(100, 80), father=prologue)
    logo_anc.plot()

    # Profile field contains card field and data field
    profile_field = Anchor(bg, 'profile field', free=(60, 500), father=prologue)
    # Card field contains appeal card and skill image
    card_field = Anchor(bg, 'card field', free=(0, 0), father=profile_field)

    ap_card_path = get_ap_card(ap_card)
    card_img = cv2.imread(ap_card_path, cv2.IMREAD_UNCHANGED)
    card_img = cv2.resize(card_img, dsize=None, fx=0.82, fy=0.82, interpolation=cv2.INTER_AREA)
    card_anc = AnchorImage(bg, 'ap card', card_img, (0, 0), father=card_field)

    skill_img = load_skill(card_img, skill)
    skill_anc = AnchorImage(bg, 'skill', skill_img, (189, 0), father=card_field)

    card_anc.plot()
    skill_anc.plot()

    # Data field contains name field and vf field
    data_field = Anchor(bg, 'profile data field', free=(0, 180), father=profile_field)

    name_bar_size = (4, 480)
    name_bar = simple_rectangle(name_bar_size, color_gray, bg.dtype)
    name_bar_anc = AnchorImage(bg, 'name bar', name_bar, free=(100, 0), father=data_field)
    parabola_gradient(name_bar, -0.65, 1.14)
    name_bar_anc.plot()

    name_field = Anchor(bg, 'name field', free=(6, 10), father=data_field)

    user_font = ImageFont.truetype(font_DFHS, 40, encoding='utf-8', index=0)
    user_anc = AnchorText(bg, 'user name', user_name, pen, user_font, free=(0, 0), father=name_field)
    id_font = ImageFont.truetype(font_DFHS, 24, encoding='utf-8', index=0)
    id_anc = AnchorText(bg, 'user id', 'ID  ' + card_num, pen, id_font, free=(50, 0), father=name_field)

    user_anc.plot(color_white)
    id_anc.plot(color_white)

    # VF field contains a vf logo and vf related texts
    vf_field = Anchor(bg, 'vf field', free=(110, 10), father=data_field)

    vf_level = get_vf_property(vol_force, is_level=True)
    force_img = cv2.imread(img_archive + 'vf/em6_' + str(vf_level).zfill(2) + '_i_eab.png', cv2.IMREAD_UNCHANGED)
    force_img = cv2.resize(force_img, dsize=None, fx=0.32, fy=0.32, interpolation=cv2.INTER_AREA)
    force_anc = AnchorImage(bg, 'volforce', force_img, free=(-20, -10), father=vf_field)

    force_anc.plot()

    # VF text field contains vf, ceil vf and floor vf
    vf_text_field = Anchor(bg, 'vf text field', free=(10, 130), father=vf_field)

    vol_font = ImageFont.truetype(font_DFHS, 30, encoding='utf-8', index=0)
    vol_anc = AnchorText(bg, 'vf text', 'VOLFORCE', pen, vol_font, free=(0, 0), father=vf_text_field)
    vol_num_font = ImageFont.truetype(font_unipace, 28, encoding='utf-8')
    vol_num_anc = AnchorText(bg, 'vf num', ('%.3f' % vol_force), pen, vol_num_font, (-1, 210), vf_text_field)
    ceil_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)
    ceil_anc = AnchorText(bg, 'ceil text', 'CEIL', pen, ceil_font, free=(50, 119), father=vf_text_field)
    floor_anc = AnchorText(bg, 'floor text', 'FLOOR', pen, ceil_font, free=(80, 89), father=vf_text_field)
    ceil_num_font = ImageFont.truetype(font_unipace, 18, encoding='utf-8')
    ceil_num_anc = AnchorText(bg, 'ceil num', ('%.3f' % ceil_num), pen, ceil_num_font, (50, 210), vf_text_field)
    floor_num_anc = AnchorText(bg, 'floor num', ('%.3f' % floor_num), pen, ceil_num_font, (80, 210), vf_text_field)

    vol_anc.plot(color_white)
    vol_num_anc.plot(get_vf_property(vol_force))
    ceil_anc.plot(color_white)
    floor_anc.plot(color_white)
    ceil_num_anc.plot(get_vf_property(ceil_num))
    floor_num_anc.plot(get_vf_property(floor_num))

    """
    Chapter 1-50: Best 50 songs
    """
    # Set data box and fonts
    box_anc = AnchorImage(bg, 'data box', box, free=(cell_gap // 2, cell_gap // 2), father=cells)

    level_font = ImageFont.truetype(font_unipace, 16, encoding='utf-8')
    title_font = ImageFont.truetype(font_DFHS, 26, encoding='utf-8', index=0)
    score_h_font = ImageFont.truetype(font_DFHS, 44, encoding='utf-8', index=0)
    score_l_font = ImageFont.truetype(font_DFHS, 32, encoding='utf-8', index=0)
    vf_str_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)
    vf_num_font = ImageFont.truetype(font_unipace, 26, encoding='utf-8')

    h_size, l_size = score_h_font.getsize('0')[0], score_l_font.getsize('0')[0]

    for index in range(50):
        # Unpack data & validity check
        is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf = music_b50[index]
        if not is_recorded:
            break

        # Box as mini background for each songs
        box_anc.set_grid((index // 2, index % 2))
        box_anc.plot()

        # Load and superimpose jacket
        jk_path = get_jacket(mid, m_type, 's')
        jk = cv2.imread(jk_path, cv2.IMREAD_UNCHANGED)
        jk = add_alpha(jk)
        jk_anc = AnchorImage(bg, 'jacket', jk, free=(8, 17), father=box_anc)
        jk_anc.plot()

        # Level box
        if m_type == '3':
            level_box = level_list[int(m_type) + int(inf_ver)]
        else:
            level_box = level_list[int(m_type)]
        level_box_anc = AnchorImage(bg, 'level box', level_box, free=(14, 144), father=box_anc)
        level_box_anc.plot()

        level_num_anc = AnchorText(bg, 'level text', lv, pen, level_font, free=(4, 76), father=level_box_anc)
        level_num_anc.plot(color_white)

        # Clear mark & grade mark
        clear_icon = clear_list[int(clear)]
        clear_anc = AnchorImage(bg, 'clear', clear_icon, free=(61, 147), father=box_anc)
        clear_anc.plot()

        grade_icon = grade_list[int(grade)]
        grade_anc = AnchorImage(bg, 'grade', grade_icon, free=(61, 202), father=box_anc)
        grade_anc.plot()

        # Title
        title = length_uni(title_font, name, length=box_x - 300)
        title_anc = AnchorText(bg, 'title', title, pen, title_font, free=(14, 271), father=box_anc)
        title_anc.plot(color_black)

        # Score contains two parts
        score_field = Anchor(bg, 'score field', free=(63, 271), father=box_anc)
        score = score.zfill(8)

        score_color = [color_black for _ in range(8)]  # Let foremost '0's be gray
        for __index in range(8):
            if score[__index] != '0':
                break
            score_color[__index] = color_gray

        high_grid = Anchor(bg, 'high num grid', free=(0, 0), father=score_field)
        high_grid.creat_grid((0, 3), (0, h_size))
        high_num_anc = AnchorText(bg, 'high num', '', pen, score_h_font, father=high_grid)
        for __index in range(0, 4):
            high_num_anc.text = score[__index]
            high_num_anc.set_grid((0, __index))
            high_num_anc.plot(score_color[__index])

        low_grid = Anchor(bg, 'low num grid', free=(10, h_size * 4), father=score_field)
        low_grid.creat_grid((0, 3), (0, l_size))
        low_num_anc = AnchorText(bg, 'low num', '', pen, score_l_font, father=low_grid)
        for __index in range(0, 4):
            low_num_anc.text = score[__index + 4]
            low_num_anc.set_grid((0, __index))
            low_num_anc.plot(score_color[__index + 4])

        # 'VF' and its value
        res_vf_field = Anchor(bg, 'respective vf field', free=(53, 485), father=box_anc)  # res = respective
        res_vf_text_anc = AnchorText(bg, 'res vf text', 'VF    #%02d' % (index + 1),
                                     pen, vf_str_font, (0, 1), res_vf_field)
        res_vf_num_anc = AnchorText(bg, 'res vf num', '%.3f' % (vf / 2), pen, vf_num_font, (22, 0), res_vf_field)

        res_vf_text_anc.plot(color_black)
        res_vf_num_anc.plot(get_vf_property(vf / 2, is_darker=True))

    """
    Epilogue: Special thanks to myself
    """
    finale_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8')
    yeast_anc = AnchorText(bg, 'yeast', 'Generated by Saccharomyces cerevisiae',
                           pen, finale_font, (20, x_px // 2), epilogue)
    yeast_anc.plot(color_gray, pos='c')

    text_layer = np.array(text_layer)
    png_superimpose(bg, text_layer)
    cv2.imwrite('%s/%s_b50_temp.png' % (output, user_name), bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

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


def plot_summary(music_map: list, profile: list, lv_base: int):
    """
         Plot function which analyzes user's record.
         :param music_map: a list of all available music records, each line of music_map should be like:
                           [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf]
                           all of them are strings, except vf is a float
         :param profile:   a list of [user_name, aka_name, ap_card, skill], all strings
         :param lv_base:   lowest level to analysis
    """

    """
    Read and initialize data
    """
    user_name, aka_name, ap_card, skill = profile  # get profile data
    music_map_sort = music_map.copy()
    music_map_sort.sort(key=lambda x: x[10], reverse=True)  # make a sorted map duplicate
    vol_force = get_overall_vf(music_map_sort[0:50])  # Get overall volforce

    # validity check for floor and ceil
    if music_map_sort[0][0]:
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
        nov, adv, exh, inf, mxm = \
            int(single_music[7]), int(single_music[10]), int(single_music[13]), \
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
    hist_list = [[[], [], [], [], [], []] for _ in range(21)]  # [[A+], [AA], [AA+], [AAA], [AAA+], [S]]
    violin_list = []  # Each line should be [score: int, lv: str]
    for record in music_map:
        if not record[0]:
            continue
        score, clear, grade, lv = int(record[3]), int(record[4]), int(record[5]), int(record[8])
        level_summary[lv][clear_index[clear]] += 1
        level_summary[lv][grade_index[grade]] += 1
        hist_list[lv][int(grade_index[grade] - 11)].append(score // 10000)
        if lv >= lv_base and score > 8000000:
            violin_list.append([score, str(lv)])
    for index in range(21):
        level_summary[index][0] = level_summary[index][6] = level_summary[index][17] - sum(level_summary[index][1:6])
    violin_df = pd.DataFrame(violin_list, columns=['score', 'lv'])

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
    # Stipulate the size of the background & generate
    px_prologue, px_chapters, px_epilogue = 450, 1625, 1950
    y_px, x_px = px_prologue + px_chapters * (21 - lv_base) + px_epilogue, 1080
    bg = generate_hex_bg((y_px, x_px))

    # Init text layer
    blank_layer = np.zeros((y_px, x_px, 3), dtype=bg.dtype)
    text_layer = Image.fromarray(blank_layer)
    text_layer.putalpha(1)
    pen = ImageDraw.Draw(text_layer)

    # Load image ingredients
    clear_ref, grade_ref, box_ref = 0, 0.45, 1.09
    clear_list, grade_list = load_clear(clear_ref), load_grade(grade_ref)
    clear_list[0] = cv2.resize(clear_list[0], dsize=None, fx=0.7, fy=0.7, interpolation=cv2.INTER_AREA)
    frame_corner, frame_side = load_frame()
    title_ing = load_bar('title', is_bg=True)
    score_ing = load_bar('name')
    horizon = cv2.imread(img_archive + 'bg/horizon.png', cv2.IMREAD_UNCHANGED) * 2
    horizon = np.repeat(horizon, 2, axis=0)

    # matplotlib & seaborn format config
    mat_font = FontProperties(fname=font_DFHS, size=12)
    sns.set_context("notebook")
    sns.set_style(style='darkgrid')
    sns.set_style(rc={'xtick.color': 'w', 'ytick.color': 'w', 'axes.labelcolor': 'w', 'font.family': ['DejaVu Sans']})

    # Genesis
    preface = Anchor(bg, 'preface')  # supreme anchor
    prologue = Anchor(bg, 'prologue', free=(0, 0), father=preface)
    chapters = Anchor(bg, 'chapters', free=(px_prologue, 0), father=preface)
    chapters.creat_grid(grid=(20 - lv_base, 0), precession=(px_chapters, 0))
    epilogue = Anchor(bg, 'epilogue', free=(y_px - px_epilogue, 0), father=preface)

    """
    Prologue: Use profile
    """
    # Profile field includes card field and name field
    profile_field = Anchor(bg, 'profile field', free=(60, 100), father=prologue)
    """
    profile_size = (340, 800)
    
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

    skill_img = load_skill(card_img, skill)
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
    frame_margin = 80
    frame_box = generate_frame(frame_corner, frame_side,
                               size=(y_px - (px_prologue + 100), x_px - frame_margin * 2),
                               width=(10, 10), color=color_d_blue, opacity=0.7)
    frame_anc = AnchorImage(bg, 'frame', img=frame_box, free=(0, frame_margin), father=chapters)
    frame_anc.plot()

    title_margin = 105
    title_bg = {'validity': True, 'image': title_ing[3], 'pos': title_ing[0].shape[1]}
    title_box = generate_bar(title_ing[0:3], x_px - title_margin * 2, title_bg)
    title_anc = AnchorImage(bg, 'title box', title_box, (25, title_margin))

    subtitle_margin = 125
    subtitle_corner = {'width': 1, 'length': 10, 'margin': 6, 'color': color_white}
    subtitle_glow = {'expand': 1, 'color': color_yellow, 'radius': 8, 'opacity': 0.3}
    subtitle_box = generate_line_box((33, x_px - subtitle_margin * 2), color_yellow, color_yellow, 1, 0.6,
                                     glow=subtitle_glow, corner=subtitle_corner)
    subtitle_anc = AnchorImage(bg, 'subtitle box', subtitle_box,
                               (0, subtitle_margin - subtitle_corner['margin']))

    data_box_length = 207
    data_box_bar = add_alpha(score_ing[1])
    data_box = bg_duplicator(data_box_bar, data_box_bar.shape[0], data_box_length)
    data_box_anc = AnchorImage(bg, 'data box', data_box)

    title_font = ImageFont.truetype(font_round, 26, encoding='utf-8')
    title_text_anc = AnchorText(bg, 'title level', '', pen, title_font, (4, 50), title_anc)
    sub_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
    subtitle_text_anc = AnchorText(bg, 'subtitle', '', pen, sub_font, (14, 16), subtitle_anc)

    icon_bg = cv2.imread(img_archive + 'grade/box_medal.png', cv2.IMREAD_UNCHANGED)
    icon_bg = cv2.resize(icon_bg, dsize=None, fx=box_ref, fy=box_ref, interpolation=cv2.INTER_AREA)
    glow_radius = 20
    icon_glow = outer_glow(icon_bg, color_l_blue, glow_radius)
    glow_anc = AnchorImage(bg, 'icon glow', icon_glow, free=(-glow_radius, -glow_radius))

    plot_bg_margin = 150
    plot_bg_glow = {'expand': 1, 'color': (0, 0, 0), 'radius': 7, 'opacity': 0.6}
    plot_bg_s_height, plot_bg_b_height = 500, 735

    plot_bg_s_size = (plot_bg_s_height, x_px - 2 * plot_bg_margin)
    plot_bg_s = generate_line_box(plot_bg_s_size, color_l_blue, (40, 59, 79), 2, 0.5, glow=plot_bg_glow, bg_img=horizon)
    plot_bg_s_anc = AnchorImage(bg, 'pie bg', plot_bg_s,
                                (20 - plot_bg_glow['radius'], plot_bg_margin - plot_bg_glow['radius']))

    plot_bg_b_size = (plot_bg_b_height, x_px - 2 * plot_bg_margin)
    plot_bg_b = generate_line_box(plot_bg_b_size, color_l_blue, (40, 59, 78), 2, 0.5, glow=plot_bg_glow, bg_img=horizon)
    plot_bg_b_anc = AnchorImage(bg, 'pie bg', plot_bg_b,
                                (20 - plot_bg_glow['radius'], plot_bg_margin - plot_bg_glow['radius']))

    sta_b_font = ImageFont.truetype(font_unipace, 30, encoding='utf-8')
    sta_s_font = ImageFont.truetype(font_unipace, 15, encoding='utf-8')

    sqrt_3, hex_y = np.sqrt(3), 36  # arrange icons in hex
    icon_x = int(2.5 * hex_y * sqrt_3)
    text_space = 210
    text_shift = (icon_x - text_space) // 2
    hex_margin = 250

    def icon_initialization(icon_list: list, name: str, dire: bool = False) -> tuple:
        icon_grid = Anchor(bg, '%s icon grid' % name)
        icon_grid.creat_grid((5, 1), (hex_y, int(hex_y * sqrt_3)))
        text_grid = Anchor(bg, '%s text grid' % name)
        text_grid.creat_grid((5, 1), (hex_y, text_space))
        content = [None, None, None, None, None, None]
        icon = [None, None, None, None, None, None]
        text_b = [None, None, None, None, None, None]
        text_s = [None, None, None, None, None, None]
        for __index in range(6):
            if dire:
                grid_id = (__index % 3 * 2 + __index // 3, __index // 3)
            else:
                grid_id = (__index % 3 * 2 + __index // 3, 1 - __index // 3)
            __bg = icon_bg.copy()
            content[__index] = AnchorImage(bg, '%s img %d' % (name, __index), __bg, father=icon_grid)
            content[__index].set_grid(grid_id)
            icon[__index] = AnchorImage(__bg, '%s icon %d' % (name, __index), icon_list[__index])
            icon[__index].plot_center(offset=(1, 1))
            text_b[__index] = \
                AnchorText(bg, '%s text big %d' % (name, __index), '', pen, sta_b_font, (7, text_shift), text_grid)
            text_b[__index].set_grid(grid_id)
            text_s[__index] = \
                AnchorText(bg, '%s text small %d' % (name, __index), '', pen, sta_s_font, (50, text_shift), text_grid)
            text_s[__index].set_grid(grid_id)
        return icon_grid, text_grid, content, text_b, text_s

    clear_grid, clear_text_grid, clear_content, clear_text_b, clear_text_s = \
        icon_initialization(clear_list, 'clear', dire=True)
    grade_grid, grade_text_grid, grade_content, grade_text_b, grade_text_s = \
        icon_initialization(grade_list[-6:], 'grade', dire=False)

    def plot_hex_icon(field: classmethod.__class__, icon_dict: dict, lv_data: list, custom: bool = False):
        icon_grid, text_grid, content, text_b, text_s = \
            icon_dict['icon'], icon_dict['text'], icon_dict['content'], icon_dict['text_b'], icon_dict['text_s']
        icon_grid.set_father(field)
        text_grid.set_father(field)
        lv_data_small, lv_cnt, lv_color = [], 0, []

        for __data in lv_data[::-1]:
            lv_cnt += __data
            lv_data_small.append('(%d)' % lv_cnt)
            if lv_cnt == lv_sum:
                lv_color.append(color_gold)
            else:
                lv_color.append(color_white)
        lv_color.reverse()
        lv_data_small.reverse()

        if custom:
            lv_data_small[0] = lv_data_small[1] = '-'

            if lv_data[0] or lv_data[1]:
                lv_color = [color_white] * 6
            lv_color[0] = lv_color[1] = color_gray

        for __index in range(6):
            content[__index].update_pos()
            data_box_anc.set_father(content[__index])
            # data_box_anc.plot(x_reverse=(content[__index].grid_id[1] == 0), offset=(27, int(hex_y * sqrt_3 * 3 / 4)))
            data_box_anc.plot(x_reverse=(content[__index].grid_id[1] == 0), offset=(0, int(hex_y * sqrt_3 * 3 / 4)))
            glow_anc.set_father(content[__index])
            glow_anc.plot()
        for __index in range(6):
            content[__index].plot()
            text_b[__index].text = str(lv_data[__index])
            text_s[__index].text = lv_data_small[__index]
            if text_b[__index].grid_id[1] == 0:
                text_b[__index].plot(lv_color[__index], pos='r')
                text_s[__index].plot(lv_color[__index], pos='r')
            else:
                text_b[__index].plot(lv_color[__index])
                text_s[__index].plot(lv_color[__index])

    def plot_pie(data_list: list, color_tuple: tuple, legend: tuple, legend_loc: tuple, size: tuple, l_col: int = 1):
        fig, ax = plt.subplots(figsize=size)
        __data_list = []
        __color_list = []

        if data_list[0]:
            wig = dict(width=0.4, edgecolor='w', lw=2)
            __data_list.append(data_list[0])
            __color_list.append(color_tuple[0])
            for __index in range(1, len(data_list)):
                if data_list[__index]:
                    __data_list.append(data_list[__index])
                    __color_list.append(color_tuple[__index])
            if len(__data_list) == 1:
                return None
            plt.pie(__data_list, radius=1, colors=__color_list, autopct='%.1f%%', pctdistance=0.8,
                    wedgeprops=wig, textprops={'fontsize': 13}, startangle=0, counterclock=False)
            plt.pie(__data_list[1:], radius=0.6, colors=__color_list[1:],
                    wedgeprops=wig, textprops={'fontsize': 13}, startangle=0, counterclock=False)
        else:
            for __index in range(len(data_list)):
                if data_list[__index]:
                    __data_list.append(data_list[__index])
                    __color_list.append(color_tuple[__index])
            wig = dict(width=0.6, edgecolor='w', lw=2)
            plt.pie(__data_list, radius=1, colors=__color_list, autopct='%.1f%%', pctdistance=0.75,
                    wedgeprops=wig, textprops={'fontsize': 14}, startangle=0, counterclock=False)

        patch = plt.pie(np.ones(len(color_tuple), dtype=int), radius=0, colors=color_tuple)[0]
        plt.legend(patch, legend, fontsize=13, loc=legend_loc, ncol=l_col)

        return fig

    def plot_histogram(data_list: list, size: tuple, legend: list or tuple, color: tuple):
        fig, ax = plt.subplots(figsize=size)
        data_all = []
        for __data in data_list:
            data_all.extend(__data)
        data_list = dict(zip(legend, data_list))

        line_kws = {"lw": 2}
        sns.histplot(data_list, palette=color, alpha=1, binwidth=2)
        sns.histplot(data_all, palette=color, alpha=0, binwidth=2, kde=True, line_kws=line_kws, color='ghostwhite')

        ax.spines['bottom'].set_color('w')
        ax.spines['top'].set_color('w')
        ax.spines['left'].set_color('w')
        ax.spines['right'].set_color('w')
        ax.tick_params(axis='x', colors='w')
        ax.tick_params(axis='y', colors='w')
        plt.xlim((900, 1000))
        plt.xticks(np.arange(900, 1001, 10), fontproperties=mat_font)
        plt.yticks(fontproperties=mat_font)
        plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.xlabel('SCORE', fontdict={'color': 'w'}, fontproperties=mat_font)
        plt.ylabel('COUNT', fontdict={'color': 'w'}, fontproperties=mat_font)

        return fig

    # Plot them by level
    for lv_index in range(21 - lv_base):
        """
        Chapter 2: Topmost level box
        """
        lv_cur = lv_index + lv_base
        lv_sum = level_summary[lv_cur][-1]
        lv_field = Anchor(bg, 'level field', father=chapters)
        lv_field.set_grid((lv_index, 0))

        title_anc.set_father(lv_field)
        title_text_anc.text = 'LV.%d' % lv_cur
        title_anc.plot()
        title_text_anc.plot(color_white)

        """
        Chapter 3: Marks
        """
        content_field = Anchor(bg, 'content', father=lv_field, free=(90, 0))
        subtitle_anc.set_father(content_field)
        subtitle_text_anc.text = 'Marks Constellation'
        subtitle_anc.plot()
        subtitle_text_anc.plot(color_white)

        clear_data = level_summary[lv_cur][:6]
        clear_field = Anchor(bg, 'clear field', father=content_field, free=(80, hex_margin))
        clear_dict = {'icon': clear_grid, 'text': clear_text_grid,
                      'content': clear_content, 'text_b': clear_text_b, 'text_s': clear_text_s}
        plot_hex_icon(clear_field, clear_dict, clear_data, custom=True)

        grade_data = level_summary[lv_cur][6:17]
        grade_hex_data = grade_data[-6:]
        grade_x = x_px - (hex_margin + icon_x)
        grade_field = Anchor(bg, 'grade_field', father=content_field, free=(80, grade_x))
        grade_dict = {'icon': grade_grid, 'text': grade_text_grid,
                      'content': grade_content, 'text_b': grade_text_b, 'text_s': grade_text_s}
        plot_hex_icon(grade_field, grade_dict, grade_hex_data)

        sum_anc = AnchorText(bg, 'sum lv.%d' % lv_cur, '/%d' % lv_sum, pen, sta_b_font, (320, x_px // 2), content_field)
        sum_anc.plot(color_white, pos='c')

        """
        Chapter 4: Pie Plot
        """
        pie_field = Anchor(bg, 'pie for two', (450, 0), father=lv_field)

        plot_bg_s_anc.set_father(pie_field)
        plot_bg_s_anc.plot()

        pie_px = (750, 400)
        pie_size = (pie_px[1] / 100, pie_px[0] / 100)

        clear_pie = plot_pie(clear_data, clear_palette, clear_legend, (0.09, 1.05), pie_size, l_col=2)
        clear_pie = get_matplotlib(clear_pie)
        clear_pie_anc = AnchorImage(bg, 'clear_pie', clear_pie, free=(-40, 140), father=pie_field)
        clear_pie_anc.plot()

        grade_pie = plot_pie(grade_data, grade_palette, grade_legend, (-0.1, -0.43), pie_size, l_col=3)
        grade_pie = get_matplotlib(grade_pie)
        grade_pie_anc = AnchorImage(bg, 'grade_pie', grade_pie, (-200, 520), father=pie_field)
        grade_pie_anc.plot()

        """
        Chapter 5: Histogram
        """
        hist_field = Anchor(bg, 'histogram', (1010, 0), father=lv_field)
        subtitle_anc.set_father(hist_field)
        subtitle_text_anc.text = 'Score Histogram'
        subtitle_anc.plot()
        subtitle_text_anc.plot(color_white)

        hist_plot_field = Anchor(bg, 'histogram plot', (30, 0), father=hist_field)
        plot_bg_s_anc.set_father(hist_plot_field)
        plot_bg_s_anc.plot(offset=(40, 0))

        hist_px = (500, 800)
        hist_size = (hist_px[1] / 100, hist_px[0] / 100)
        hist_data = hist_list[lv_cur]
        hist = plot_histogram(hist_data, hist_size, grade_legend[-6:], grade_palette[-6:])
        hist = get_matplotlib(hist)
        hist_anc = AnchorImage(bg, 'histogram', hist, (50, 150), father=hist_plot_field)
        hist_anc.plot()

    """
    Epilogue: Joint plot and violin plot
    """
    sns.set_context("talk")

    title_anc.set_father(epilogue)
    title_text_anc.text = 'Panorama'
    title_anc.plot()
    title_text_anc.plot(color_white)

    def plot_joint(data_frame: pd.DataFrame, size: float, palette: tuple):
        fig, ax = plt.subplots(figsize=(size, size))
        x_lim_low = low_score // 100000 * 100000
        if palette is not None:
            palette = list(palette)
            palette.reverse()
        plot = sns.jointplot(data=data_frame, hue='lv', x='score', y='vf', height=size, xlim=(x_lim_low, 10000000),
                             ylim=(low_vf - 0.2, high_vf + 0.2), alpha=0.8, palette=palette, marginal_ticks=True)
        plot.set_axis_labels('SCORE', 'VOLFORCE', fontsize=12)

        return fig

    def plot_violin(data_frame: pd.DataFrame, size: tuple, palette: tuple):
        fig, ax = plt.subplots(figsize=size)
        pale = None
        if palette is not None:
            pale = []
            for color in palette:
                int_color = hex_2_rgb(color)
                pale_grey = (128, 128, 128)
                pale_color = (np.array(int_color) + np.array(pale_grey) * 2) // 3
                pale.append(rgb_2_hex(pale_color))
        sns.violinplot(data=data_frame, x='lv', y='score', inner=None, color='.8', palette=pale)
        sns.stripplot(data=data_frame, x='lv', y='score', palette=palette)

        plt.ylabel('SCORE', fontproperties=mat_font)
        plt.xlabel('LEVEL', fontproperties=mat_font)
        plt.xticks(fontproperties=FontProperties(fname=font_DFHS, size=16))
        plt.yticks([8700000, 9000000, 9300000, 9500000, 9700000, 9800000, 9900000, 10000000],
                   [870, 900, 930, 950, 970, 980, 990, 1000], fontproperties=mat_font)
        return fig

    if lv_base > 14:
        plot_palette = level_palette[lv_base - 21:]
    else:
        plot_palette = None

    # Joint plot for vf-score
    joint_field = Anchor(bg, 'joint field', father=epilogue, free=(90, 0))

    subtitle_anc.set_father(joint_field)
    subtitle_text_anc.text = 'VF-Score Joint Plot'
    subtitle_anc.plot()
    subtitle_text_anc.plot(color_white)

    joint_plot_field = Anchor(bg, 'joint plot field', father=joint_field, free=(30, 0))
    plot_bg_b_anc.set_father(joint_plot_field)
    plot_bg_b_anc.plot(offset=(40, 0))

    joint_px = 740
    joint_size = joint_px / 100
    joint = plot_joint(vf_df, joint_size, plot_palette)
    joint = get_matplotlib(joint)
    joint_anc = AnchorImage(bg, 'joint plot', joint, free=(68, 170), father=joint_plot_field)
    joint_anc.plot()

    # Violin plot for score distribution
    violin_field = Anchor(bg, 'violin field', father=epilogue, free=(955, 0))

    subtitle_anc.set_father(violin_field)
    subtitle_text_anc.text = 'Score Distribution Violin Plot'
    subtitle_anc.plot()
    subtitle_text_anc.plot(color_white)

    violin_plot_field = Anchor(bg, 'violin plot field', father=violin_field, free=(30, 0))
    plot_bg_b_anc.set_father(violin_plot_field)
    plot_bg_b_anc.plot(offset=(40, 0))

    violin_px = (800, 800)
    violin_size = (violin_px[1] / 100, violin_px[0] / 100)
    violin = plot_violin(violin_df, violin_size, plot_palette)
    violin = get_matplotlib(violin)
    violin_anc = AnchorImage(bg, 'violin plot', violin, free=(0, 170), father=violin_plot_field)
    violin_anc.plot()

    finale_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8')
    finale_anc = Anchor(bg, 'finale', (px_epilogue - 75, x_px // 2), epilogue)
    yeast_anc = AnchorText(bg, 'yeast', 'Generated by Saccharomyces cerevisiae', pen, finale_font, (0, 0), finale_anc)
    author_anc = AnchorText(bg, 'author', 'Powered by Nyanm & Achernar', pen, finale_font, (30, 0), finale_anc)
    yeast_anc.plot(color_gray, pos='c')
    author_anc.plot(color_gray, pos='c')

    text_layer = np.array(text_layer)
    png_superimpose(bg, text_layer)
    cv2.imwrite('%s/%s_summary_beta.png' % (output, user_name), bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])
    print('Plot successfully.')

    msg = '----------------Level Summary----------------\n' \
          'Level    NC      HC      UC      PUC     ||    AAA     AAA+    S     ||      SUM\n'
    for index in range(lv_base, 21):
        nc, hc, uc, puc = level_summary[index][2:6]
        aaa, aaa_plus, s, __sum = level_summary[index][14:]
        msg += ('lv.%d    ' % index)
        msg += ('%-8d%-8d%-8d%-8d||    %-8d%-8d%-8d||    %-8d\n' % (nc, hc, uc, puc, aaa, aaa_plus, s, __sum))

    print(msg)

    try:
        remove(local_dir + '/data/matplotlib.png')
    except FileNotFoundError:
        pass
