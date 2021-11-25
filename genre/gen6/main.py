from .tools import *
import pandas as pd
import seaborn as sns
from os import remove
from traceback import format_exc
from matplotlib.ticker import MaxNLocator
from matplotlib.font_manager import FontProperties


def plot_single(music_map: list, profile: list, sg_index: int) -> str:
    """
    Plot function for single record
    Now Plot function is ongoing, again.
    :param music_map: a list contains all music records, each line of music_map should be:
                      [is_record, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf, exscore]
                      Please check music_map for explicit definition.
    :param profile:   a list of [user_name, ap_card, aka_index, skill, crew_id]
    :param sg_index:  the index of THE record in music_map
    :return:          text data of single record
    """

    """
    Unfold data and generate text message
    """
    record = music_map[sg_index]
    id_recorded, mid, m_type, score, clear, grade, m_time, name, lv, inf_ver, vf, exscore = record
    user_name, ap_card, aka_index, skill, crew_id = profile
    diff = get_diff(m_type, inf_ver)
    real_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m_time / 1000))

    # Get recent text message
    msg = '|Date                 |Diff  |Score    |Grade |Clear |VF     |Name\n|%-21s|%-6s|%-9s|%-6s|%-6s|%.3f |%s\n' \
          % (real_time, (diff + lv), score, grade_table[grade], clear_table[clear], vf / 2, name)
    timber.info('Generate single data complete.\n\n%s\n' % msg)

    try:
        """
        Preparation for b50 and single record data
        """
        __level_table = np.load(local_dir + '/data/level_table.npy')
        single_data = __level_table[mid]

        music_map.sort(key=lambda x: x[10], reverse=True)
        music_b50 = music_map[:50]
        vf_floor = music_b50[-1][10]
        vol_force = get_overall_vf(music_b50)

        rank = 0
        for record in music_map:
            rank += 1
            if vf >= record[10]:
                break

        """
        Initialize background
        """
        # The very background which is pure black
        y_px, x_px = 1920, 1080
        bg = np.zeros((y_px, x_px, 3), dtype=np.uint8)
        bg = add_alpha(bg)

        # Init text layer
        blank_layer = np.ones((y_px, x_px, 3), dtype=bg.dtype) * 255  # There must be something wrong in PIL ImageFont
        text_layer = Image.fromarray(blank_layer)
        text_layer.putalpha(1)
        pen = ImageDraw.Draw(text_layer)

        # The gen6 background
        game_bg = cv2.imread(img_archive + '/shutter/bg.png', cv2.IMREAD_UNCHANGED)
        bg_y, bg_x, chn = game_bg.shape
        bg_ratio = y_px / bg_y
        game_bg = cv2.resize(game_bg, dsize=None, fx=bg_ratio, fy=bg_ratio, interpolation=cv2.INTER_AREA)
        png_superimpose(bg, game_bg, (0, 0))

        bg_anc = Anchor(bg, 'THE bg', (0, 0))

        """
        From top to bottom
        """
        jk = get_jacket(mid, m_type, size='b')

        # Main body of side bar
        side_bar = cv2.imread(img_archive + '/ms_sel/bg_sel_i_feb.png', cv2.IMREAD_UNCHANGED)
        side_bar_y, side_bar_x, chn = side_bar.shape
        side_field = Anchor(bg, 'side field', (y_px - side_bar_y, 0), father=bg_anc)
        side_anc = AnchorImage(bg, 'side bar', side_bar, (0, 0), father=side_field)

        # Background jacket
        jk_factor = 1.43
        jk_bg = cv2.resize(jk, dsize=None, fx=jk_factor, fy=jk_factor, interpolation=cv2.INTER_AREA)
        jk_bg_y, jk_bg_x, chn = jk_bg.shape
        jk_bg = jk_bg[:, abs(jk_bg_x - side_bar_x) // 2:, :]
        jk_bg_anc = AnchorImage(bg, 'jk bg', jk_bg, (0, 0), father=bg_anc)

        jk_bg_anc.plot()
        side_anc.plot()

        # Cyan glow on side bar
        side_glow = cv2.imread(img_archive + '/ms_sel/glow_blue3.png', cv2.IMREAD_UNCHANGED)
        glow_anc = AnchorImage(bg, 'glow', side_glow, (254, 0), father=side_field)
        glow_anc.plot()

        # Jacket box and jacket itself
        jk_box = cv2.imread(img_archive + '/ms_sel/box_jk.png', cv2.IMREAD_UNCHANGED)
        jk_box_anc = AnchorImage(bg, 'jk box', jk_box, (136, 52), father=side_field)
        jk_box_anc.plot()

        jk_ratio = 350 / jk.shape[0]
        jk = cv2.resize(jk, dsize=None, fx=jk_ratio, fy=jk_ratio, interpolation=cv2.INTER_AREA)
        jk_anc = AnchorImage(bg, 'jk img', jk, (44, 44), father=jk_box_anc)
        jk_anc.plot()

        # If this song is one of your best 50s
        if vf >= vf_floor:
            b50 = cv2.imread(img_archive + '/ms_sel/scouter_b_1.png', cv2.IMREAD_UNCHANGED)
            b50_anc = AnchorImage(bg, 'b50', b50, (249, 43), father=jk_box_anc)
            b50_anc.plot()

            vol_force = get_overall_vf(music_map[:50])
            vf_icon = load_vf(vol_force, is_small=True)
            vf_factor = 0.45
            vf_icon = cv2.resize(vf_icon, dsize=None, fx=vf_factor, fy=vf_factor, interpolation=cv2.INTER_AREA)
            vf_icon_anc = AnchorImage(bg, 'vf icon', vf_icon, (92, 5), b50_anc)
            vf_icon_anc.plot()

        # Grade hex box and icon
        grade_box = cv2.imread(img_archive + '/ms_sel/box_medal.png', cv2.IMREAD_UNCHANGED)
        grade_box_anc = AnchorImage(bg, 'grade box', grade_box, (617, 345), father=side_field)
        grade_box_anc.plot()

        grade_icon = cv2.imread(img_archive + '/ms_sel/grade_%s.png' % grade_img[grade], cv2.IMREAD_UNCHANGED)
        grade_factor = 0.43
        grade_icon = cv2.resize(grade_icon, dsize=None, fx=grade_factor, fy=grade_factor, interpolation=cv2.INTER_AREA)
        grade_anc = AnchorImage(bg, 'grade', grade_icon, free=(11, 13), father=grade_box_anc)
        grade_anc.plot()

        # Clear base, hex box and icon
        clear_base = cv2.imread(img_archive + '/ms_sel/hex_base.png', cv2.IMREAD_UNCHANGED)
        clear_base_anc = AnchorImage(bg, 'clear base', clear_base, (648, 413), father=side_field)
        clear_base_anc.plot()

        clear_box = cv2.imread(img_archive + '/ms_sel/hex_base2.png', cv2.IMREAD_UNCHANGED)
        box_factor = 1.07
        clear_box = cv2.resize(clear_box, dsize=None, fx=box_factor, fy=box_factor, interpolation=cv2.INTER_AREA)
        clear_box_anc = AnchorImage(bg, 'clear box', clear_box, free=(-107, -28), father=clear_base_anc)
        clear_box_anc.plot()

        clear_icon = cv2.imread(img_archive + '/ms_sel/mark_%s.png' % clear_img[clear], cv2.IMREAD_UNCHANGED)
        clear_factor = 1.09
        clear_icon = cv2.resize(clear_icon, dsize=None, fx=clear_factor, fy=clear_factor, interpolation=cv2.INTER_AREA)
        clear_icon_anc = AnchorImage(bg, 'clear icon', clear_icon, free=(-68, 12), father=clear_base_anc)
        clear_icon_anc.plot()

        # "Best" light, cuz Asphyxia only records best record
        best = cv2.imread(img_archive + '/ms_sel/text_bestscore2.png', cv2.IMREAD_UNCHANGED)
        best_anc = AnchorImage(bg, 'best light', best, (608, 15), father=side_field)
        best_anc.plot()

        # Score, both bigger four and smaller four
        score = str(score).zfill(8)
        is_trans, opacity = 1, 0.5

        bigger_anc = Anchor(bg, 'big four', free=(629, 38), father=side_field)
        bigger_anc.creat_grid((0, 3), (0, 42))
        b_factor = 0.69
        for index in range(4):  # Bigger four
            num = score[index]
            if num != '0':
                is_trans = 0
            cur_num = cv2.imread(img_archive + '/psd_num/num_score_%s.png' % num, cv2.IMREAD_UNCHANGED)
            cur_num = cv2.resize(cur_num, dsize=None, fx=b_factor, fy=b_factor, interpolation=cv2.INTER_AREA)
            cur_anc = AnchorImage(bg, 'b_num #%d %s' % (index, num), cur_num, father=bigger_anc)
            cur_anc.set_grid((0, index))
            cur_anc.plot(opacity=(1 - is_trans * opacity))

        s_factor = 0.46
        smaller_anc = Anchor(bg, 'small four', free=(642, 207), father=side_field)
        smaller_anc.creat_grid((0, 3), (0, 30))
        for index in range(4, 8):  # Smaller four
            num = score[index]
            if num != '0':
                is_trans = 0
            cur_num = cv2.imread(img_archive + '/psd_num/num_score_%s.png' % num, cv2.IMREAD_UNCHANGED)
            cur_num = cv2.resize(cur_num, dsize=None, fx=s_factor, fy=s_factor, interpolation=cv2.INTER_AREA)
            cur_anc = AnchorImage(bg, 's_num #%d %s' % (index, num), cur_num, father=smaller_anc)
            cur_anc.set_grid((0, index - 4))
            cur_anc.plot(opacity=(1 - is_trans * opacity))

        # EX score
        ex_rate_font = ImageFont.truetype(font_continuum, 15, encoding='utf-8')
        if exscore:
            # Ex score box
            ex_box = cv2.imread(img_archive + '/ms_sel/ex_score.png', cv2.IMREAD_UNCHANGED)
            ex_anc = AnchorImage(bg, 'ex box', ex_box, (680, 21), father=side_field)
            ex_anc.plot()

            # The exscore itself
            exscore_anc = AnchorText(bg, 'exscore', str(exscore), pen, ex_rate_font, (5, 151), ex_anc)
            exscore_anc.plot((120, 79, 26), pos='r')

        # Clear rate and number
        rate_box = cv2.imread(img_archive + '/ms_sel/text_clearrate.png', cv2.IMREAD_UNCHANGED)
        rate_anc = AnchorImage(bg, 'rate box', rate_box, (680, 181), father=side_field)
        rate_anc.plot()

        rate_num = '99.61'
        rate_num_anc = AnchorText(bg, 'rate', rate_num, pen, ex_rate_font, (5, 140), rate_anc)
        rate_num_anc.plot((255, 255, 255), pos='r')

        # BPM box
        bpm_box = cv2.imread(img_archive + '/ms_sel/box_bpm.png', cv2.IMREAD_UNCHANGED)
        bpm_anc = AnchorImage(bg, 'bpm box', bpm_box, (759, 22), father=side_field)
        bpm_anc.plot()

        bpm_font = ImageFont.truetype(font_continuum, 20, encoding='utf-8')
        bpm_str = get_bpm_str(single_data[5], single_data[6])
        bpm_str_anc = AnchorText(bg, 'bpm', bpm_str, pen, bpm_font, (3, 53), bpm_anc)
        bpm_str_anc.plot((255, 255, 255))

        # Safe icon
        safe = cv2.imread(img_archive + '/ms_sel/icon_safe.png', cv2.IMREAD_UNCHANGED)
        safe_anc = AnchorImage(bg, 'safe', safe, (766, 237), father=side_field)
        safe_anc.plot()

        # Song name and artist
        name_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8')
        song_name = length_uni(name_font, single_data[1], 500)
        artist = length_uni(name_font, single_data[3], 500)
        name_anc = AnchorText(bg, 'name', song_name, pen, name_font, (804, 34), side_field)
        artist_anc = AnchorText(bg, 'artist', artist, pen, name_font, (845, 34), side_field)

        name_anc.plot((255, 255, 255))
        artist_anc.plot((255, 255, 255))

        # Level boxes
        level_anc = Anchor(bg, 'level grid', free=(900, 46), father=side_field)
        level_anc.creat_grid((0, 3), (0, 116))
        cursor = cv2.imread(img_archive + '/ms_sel/cursor_level.png', cv2.IMREAD_UNCHANGED)
        cursor_factor = 0.82
        cursor = cv2.resize(cursor, dsize=None, fx=cursor_factor, fy=cursor_factor, interpolation=cv2.INTER_AREA)
        lv_list = [single_data[10], single_data[13], single_data[16], str(int(single_data[19]) + int(single_data[22]))]

        if m_type == 5:
            cursor_index = 4
        else:
            cursor_index = m_type

        for index in range(4):
            cur_lv = lv_list[index].zfill(2)
            if not int(cur_lv):
                continue

            lv_field = Anchor(bg, 'level box', free=(12, 23), father=level_anc)
            lv_field.set_grid((0, index))

            if cursor_index == index:
                cursor_anc = AnchorImage(bg, 'cursor', cursor, free=(-15, -33), father=lv_field)
                cursor_anc.plot()

            lv_left = cv2.imread(img_archive + '/psd_num/num_level_%s.png' % cur_lv[0], cv2.IMREAD_UNCHANGED)
            lv_right = cv2.imread(img_archive + '/psd_num/num_level_%s.png' % cur_lv[1], cv2.IMREAD_UNCHANGED)
            left_anc = AnchorImage(bg, 'lv left', lv_left, free=(0, 0), father=lv_field)
            right_anc = AnchorImage(bg, 'lv right', lv_right, free=(0, 29), father=lv_field)

            if index <= 2:  # NOV, ADV, EXH
                lv_text = diff_text_table[index + 1]
            elif int(single_data[9]):  # INF, GRV, HVN, VVD
                lv_text = diff_text_table[index + int(inf_ver) - 1]
            else:  # MXM
                lv_text = diff_text_table[8]
            lv_text = cv2.imread(img_archive + '/psd_level/level_sel_%s.png' % lv_text, cv2.IMREAD_UNCHANGED)
            lv_text_anc = AnchorImage(bg, 'level text', lv_text, free=(56, -11), father=lv_field)

            left_anc.plot()
            right_anc.plot()
            lv_text_anc.plot()

        # Effector box and Illustrator box
        eff_ill_font = ImageFont.truetype(font_DFHS, 16, encoding='utf-8')

        eff_box = cv2.imread(img_archive + '/ms_sel/box_effected.png', cv2.IMREAD_UNCHANGED)
        eff_anc = AnchorImage(bg, 'eff box', eff_box, free=(1019, 90), father=side_field)
        eff = length_uni(eff_ill_font, single_data[12 + m_type * 3], 250)
        eff_text_anc = AnchorText(bg, 'eff text', eff, pen, eff_ill_font, free=(7, 162), father=eff_anc)

        eff_anc.plot()
        eff_text_anc.plot((255, 255, 255))

        ill_box = cv2.imread(img_archive + '/ms_sel/box_illustrated.png', cv2.IMREAD_UNCHANGED)
        ill_anc = AnchorImage(bg, 'ill box', ill_box, free=(1052, 90), father=side_field)
        ill = length_uni(eff_ill_font, single_data[11 + m_type * 3], 250)
        ill_text_anc = AnchorText(bg, 'ill text', ill, pen, eff_ill_font, free=(7, 162), father=ill_anc)

        ill_anc.plot()
        ill_text_anc.plot((255, 255, 255))

        """
        Set up user profile
        """
        # Time for Saccharomyces cerevisiae
        yeast_field = Anchor(bg, 'yeast field', free=(1230, 0), father=bg_anc)
        yeast_font = ImageFont.truetype(font_DFHS, 18, encoding='utf-8')
        yeast_bg = simple_rectangle((350, x_px), (0, 0, 0), np.uint8)
        yeast_bg_anc = AnchorImage(bg, 'yeast bg', yeast_bg, free=(10, 0), father=yeast_field)
        yeast_anc = AnchorText(bg, 'yeast', 'Generated by Saccharomyces cerevisiae', pen, yeast_font,
                               free=(300, 270), father=yeast_field)

        yeast_bg_anc.plot(0.65)
        yeast_anc.plot(color_gray, pos='c')

        profile_img = generate_mini_profile(profile, vol_force, [vf / 2, rank, real_time])
        profile_anc = AnchorImage(bg, 'profile', profile_img, (40, (540 - profile_img.shape[1]) // 2), yeast_field)
        profile_anc.plot()

        text_layer = np.array(text_layer)
        png_superimpose(bg, text_layer)
        output_path = '%s/%s_%s%s.png' % (cfg.output, validate_filename(user_name), mid, diff)
        cv2.imwrite(output_path, bg[:1560, :540, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

        timber.info_show('Plot saved at [%s] successfully.' % output_path)

        return msg

    except Exception:
        timber.warning('Something wrong happens in the plot function, only will the text message be returned.\n\n%s\n'
                       % format_exc())
        return msg


def plot_b50(music_map: list, profile: list) -> str:
    """
    Plot function for best 50 records
    :param music_map: a list contains all music records, each line of music_map should be:
                      [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf, exscore]
                      Please check music_map for explicit definition.
    :param profile:   a list of [user_name, aka_name, ap_card, skill], all strings
    :return:          text data of best 50
    """

    """
    Read and initialize data
    """
    # Unpack profile data & sort music records
    user_name, ap_card, aka_name, skill, crew_id = profile
    music_map.sort(key=lambda x: x[10], reverse=True)
    music_b50 = music_map[:50]
    vol_force = get_overall_vf(music_b50)  # Get overall volforce

    """
    Generate text message before any wrong would happen
    """
    msg = ''
    msg += ('----------------VOLFORCE %.3f----------------\n' % vol_force)
    msg += 'No.  VF      DIFF   SCORE    RANK  LHT  NAME\n'
    for index in range(50):
        diff = get_diff(music_b50[index][2], music_b50[index][9])
        msg += ('#%-4d%.3f  %s%-2s  %-9s%-6s%-5s%s\n' % ((index + 1), music_b50[index][10] / 2, diff,
                                                         music_b50[index][8], music_b50[index][3],
                                                         clear_table[music_b50[index][4]],
                                                         grade_table[music_b50[index][5]], music_b50[index][7]))
    timber.info('Generate B50 data complete.\n\n%s\n' % msg)

    try:  # If the plot module breaks down somehow, the function will try to return the pure text data.
        """
        Generate background, text layer and load image ingredients
        """
        # Stipulate the size of the background & generate
        px_prologue, px_chapters, px_epilogue = 430, 144, 70
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
        box = cv2.imread(img_archive + '/bg/box_semi.png', cv2.IMREAD_UNCHANGED)
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
        Prologue: User profile
        """

        std_profile = generate_std_profile(profile, vol_force)
        profile_anc = AnchorImage(bg, 'profile', std_profile, (30, (x_px - std_profile.shape[1]) // 2), father=prologue)
        profile_anc.plot()

        """
        Chapter 1-50: Best 50 songs
        """
        # Set data box and fonts
        box_anc = AnchorImage(bg, 'data box', box, free=(cell_gap // 2, cell_gap // 2), father=cells)

        level_font = ImageFont.truetype(font_continuum, 17, encoding='utf-8')
        title_font = ImageFont.truetype(font_DFHS, 26, encoding='utf-8', index=0)
        score_h_font = ImageFont.truetype(font_DFHS, 44, encoding='utf-8', index=0)
        score_l_font = ImageFont.truetype(font_DFHS, 32, encoding='utf-8', index=0)
        vf_str_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)
        vf_num_font = ImageFont.truetype(font_continuum, 29, encoding='utf-8')

        h_size, l_size = score_h_font.getsize('0')[0], score_l_font.getsize('0')[0]

        for index in range(50):
            # Unpack data & validity check
            is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf, exs = music_b50[index]
            if not is_recorded:
                break

            # Box as mini background for each songs
            box_anc.set_grid((index // 2, index % 2))
            box_anc.plot()

            # Load and superimpose jacket
            jk = get_jacket(mid, m_type, 's')
            jk_anc = AnchorImage(bg, 'jacket', jk, free=(8, 17), father=box_anc)
            jk_anc.plot()

            # Level box
            if m_type == 3:
                level_box = level_list[m_type + int(inf_ver)]
            else:
                level_box = level_list[m_type]
            level_box_anc = AnchorImage(bg, 'level box', level_box, free=(14, 144), father=box_anc)
            level_box_anc.plot()

            level_num_anc = AnchorText(bg, 'level text', lv, pen, level_font, free=(2, 76), father=level_box_anc)
            level_num_anc.plot(color_white)

            # Clear mark & grade mark
            clear_icon = clear_list[clear]
            clear_anc = AnchorImage(bg, 'clear', clear_icon, free=(61, 147), father=box_anc)
            clear_anc.plot()

            grade_icon = grade_list[grade]
            grade_anc = AnchorImage(bg, 'grade', grade_icon, free=(61, 202), father=box_anc)
            grade_anc.plot()

            # Title
            title = length_uni(title_font, name, length=box_x - 300)
            title_anc = AnchorText(bg, 'title', title, pen, title_font, free=(14, 271), father=box_anc)
            title_anc.plot(color_black)

            # Score contains two parts
            score_field = Anchor(bg, 'score field', free=(63, 271), father=box_anc)
            score = str(score).zfill(8)

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
            res_vf_field = Anchor(bg, 'respective vf field', free=(53, 488), father=box_anc)  # res = respective
            res_vf_text_anc = AnchorText(bg, 'res vf text', 'VF   #%02d' % (index + 1),
                                         pen, vf_str_font, (0, 1), res_vf_field)
            res_vf_num_anc = AnchorText(bg, 'res vf num', '%.3f' % (vf / 2), pen, vf_num_font, (20, -5), res_vf_field)

            res_vf_text_anc.plot(color_black)
            res_vf_num_anc.plot(get_vf_level(vf / 2, is_darker=True, is_color=True))

        """
        Epilogue: Special thanks to myself
        """
        finale_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8')
        yeast_anc = AnchorText(bg, 'yeast', 'Generated by Saccharomyces cerevisiae',
                               pen, finale_font, (20, x_px // 2), epilogue)
        yeast_anc.plot(color_gray, pos='c')

        text_layer = np.array(text_layer)
        png_superimpose(bg, text_layer)
        output_path = '%s/%s_B50.png' % (cfg.output, validate_filename(user_name))
        cv2.imwrite(output_path, bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

        timber.info_show('Plot saved at [%s] successfully.' % output_path)
        return msg

    except Exception:
        timber.warning('Something wrong happens in the plot function, only will the text message be returned.\n\n%s\n'
                       % format_exc())
        return msg


def plot_level(music_map: list, profile: list, level: int, threshold: int):
    """
    Plot function to list single level records (above a specific score)
    """
    user_name, ap_card, aka_name, skill, crew_id = profile
    lv_map = []
    for record in music_map:
        if int(record[8]) == level and record[3] >= threshold:
            lv_map.append(record)

    lv_map.sort(key=lambda x: x[3], reverse=True)
    length = len(lv_map)
    msg = '|Level.%d       |Threshold = %d\n|No.  |Score    |Grade |Clear |VF     |Name\n' % (level, threshold)
    for index in range(length):
        record = lv_map[index]
        msg += '|%-5d|%-9s|%-6s|%-6s|%.3f |%s\n' % \
               (index + 1, record[3], grade_table[record[5]], clear_table[record[4]], record[10], record[7])
    timber.info('Generate level.%d scores complete.\n\n%s\n' % (level, msg))

    try:
        music_map.sort(key=lambda x: x[10], reverse=True)
        music_b50 = music_map[:50]
        vol_force = get_overall_vf(music_b50)

        """
        Generate ingredients
        """
        # Stipulate the size of the background & generate
        px_prologue, px_chapters, px_epilogue = 140, 144, 70
        y_px, x_px = px_prologue + px_chapters * (length // 2 + 1) + px_epilogue, 1280
        bg = generate_hex_bg((y_px, x_px))

        # Init text layer
        blank_layer = np.ones((y_px, x_px, 3), dtype=np.uint8) * 154  # Makeshift
        text_layer = Image.fromarray(blank_layer)
        text_layer.putalpha(1)
        pen = ImageDraw.Draw(text_layer)

        # Load image ingredients
        level_ref, clear_ref, grade_ref = 0, 0.58, 0.42
        level_list, clear_list, grade_list = load_level(level_ref), load_clear(clear_ref), load_grade(grade_ref)
        box = cv2.imread(img_archive + '/bg/box_semi.png', cv2.IMREAD_UNCHANGED)
        box_y, box_x, chn = box.shape

        # Genesis
        preface = Anchor(bg, 'preface')  # supreme anchor
        prologue = Anchor(bg, 'prologue', free=(0, 0), father=preface)
        chapters = Anchor(bg, 'chapter', free=(px_prologue, 0), father=preface)

        cell_gap = 20  # Cell gap defines who far between two adjacent boxes, both x axis and y axis
        cell_margin = (x_px - 2 * (box_x + cell_gap)) // 2
        cells = Anchor(bg, 'cells', free=(0, cell_margin), father=chapters)
        cells.creat_grid(((length // 2 + 1), 1), (px_chapters, box_x + cell_gap))

        epilogue = Anchor(bg, 'epilogue', free=(y_px - px_epilogue, 0), father=preface)

        """
        Prologue: User profile
        """
        # Profile
        profile_img = generate_mini_profile(profile, vol_force)
        profile_margin = cell_gap // 2 + cell_margin + (box_x - profile_img.shape[1]) // 2
        profile_anc = AnchorImage(bg, 'profile', profile_img, (30, profile_margin), father=prologue)
        profile_anc.plot()

        # Level title
        title_ing = load_bar('title', is_bg=True)
        title_bg = {'validity': True, 'image': title_ing[3], 'pos': title_ing[0].shape[1]}
        title_box = generate_bar(title_ing[0:3], box_x, title_bg)
        title_anc = AnchorImage(bg, 'title box', title_box, (55, (x_px + cell_margin) // 2), father=preface)
        title_anc.plot()

        title_font = ImageFont.truetype(font_continuum, 28, encoding='utf-8')
        title_text = AnchorText(bg, 'title', 'LEVEL %d    Threshold = %d' % (level, threshold),
                                pen, title_font, (4, 52), title_anc)
        title_text.plot(color_white)

        """
        Chapter 1-?
        """
        # Set data box and fonts
        box_anc = AnchorImage(bg, 'data box', box, free=(cell_gap // 2, cell_gap // 2), father=cells)

        level_font = ImageFont.truetype(font_continuum, 17, encoding='utf-8')
        title_font = ImageFont.truetype(font_DFHS, 26, encoding='utf-8', index=0)
        score_h_font = ImageFont.truetype(font_DFHS, 44, encoding='utf-8', index=0)
        score_l_font = ImageFont.truetype(font_DFHS, 32, encoding='utf-8', index=0)
        vf_str_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8', index=0)
        vf_num_font = ImageFont.truetype(font_continuum, 29, encoding='utf-8')

        h_size, l_size = score_h_font.getsize('0')[0], score_l_font.getsize('0')[0]

        for index in range(length):
            is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf, exs = lv_map[index]

            box_anc.set_grid((((index + 1) // 2), (1 - index % 2)))
            box_anc.plot()

            # Load and superimpose jacket
            jk = get_jacket(mid, m_type, 's')
            jk_anc = AnchorImage(bg, 'jacket', jk, free=(8, 17), father=box_anc)
            jk_anc.plot()

            # Level box
            if m_type == 3:
                level_box = level_list[m_type + int(inf_ver)]
            else:
                level_box = level_list[m_type]
            level_box_anc = AnchorImage(bg, 'level box', level_box, free=(14, 144), father=box_anc)
            level_box_anc.plot()

            level_num_anc = AnchorText(bg, 'level text', lv, pen, level_font, free=(2, 76), father=level_box_anc)
            level_num_anc.plot(color_white)

            # Clear mark & grade mark
            clear_icon = clear_list[clear]
            clear_anc = AnchorImage(bg, 'clear', clear_icon, free=(61, 147), father=box_anc)
            clear_anc.plot()

            grade_icon = grade_list[grade]
            grade_anc = AnchorImage(bg, 'grade', grade_icon, free=(61, 202), father=box_anc)
            grade_anc.plot()

            # Title
            title = length_uni(title_font, name, length=box_x - 300)
            title_anc = AnchorText(bg, 'title', title, pen, title_font, free=(14, 271), father=box_anc)
            title_anc.plot(color_black)

            # Score contains two parts
            score_field = Anchor(bg, 'score field', free=(63, 271), father=box_anc)
            score = str(score).zfill(8)

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
            res_vf_field = Anchor(bg, 'respective vf field', free=(53, 488), father=box_anc)  # res = respective
            res_vf_text_anc = AnchorText(bg, 'res vf text', 'SCORE    #%03d' % (index + 1),
                                         pen, vf_str_font, (0, -97), res_vf_field)
            res_vf_num_anc = AnchorText(bg, 'res vf num', '%.3f' % (vf / 2), pen, vf_num_font, (20, -5), res_vf_field)

            res_vf_text_anc.plot(color_black)
            res_vf_num_anc.plot(get_vf_level(vf / 2, is_darker=True, is_color=True))

        """
        Epilogue: Special thanks to myself
        """
        finale_font = ImageFont.truetype(font_DFHS, 20, encoding='utf-8')
        yeast_anc = AnchorText(bg, 'yeast', 'Generated by Saccharomyces cerevisiae',
                               pen, finale_font, (20, x_px // 2), epilogue)
        yeast_anc.plot(color_gray, pos='c')

        text_layer = np.array(text_layer)
        png_superimpose(bg, text_layer)
        output_path = '%s/%s_LEVEL%d@%d.png' % (cfg.output, validate_filename(user_name), level, threshold)
        cv2.imwrite(output_path, bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])
        timber.info_show('Plot saved at [%s] successfully.' % output_path)

        return msg

    except Exception:
        timber.warning('Something wrong happens in the plot function, only will the text message be returned.\n\n%s\n'
                       % format_exc())
        return msg


def plot_summary(music_map: list, profile: list, lv_base: int):
    """
    Plot function to analyze user's record.
    :param music_map: a list of all available music records, each line of music_map should be like:
                      [is_recorded, mid, m_type, score, clear, grade, timestamp, name, lv, inf_ver, vf, exscore]
                      Please check music_map for explicit definition.
    :param profile:   a list of [user_name, aka_name, ap_card, skill], all strings
    :param lv_base:   lowest level to analysis
    :return:          text data of summary
    """

    """
    Read and initialize data
    """
    user_name, ap_card, akaname, skill, crew_id = profile  # get profile data
    music_map_sort = music_map.copy()
    music_map_sort.sort(key=lambda x: x[10], reverse=True)  # make a sorted map duplicate
    vol_force = get_overall_vf(music_map_sort[0:50])  # Get overall volforce

    level_summary = np.zeros((21, 18), dtype=int)  # Get default level summary
    clear_index = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    grade_index = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 11, 6: 12, 7: 13, 8: 14, 9: 15, 10: 16}
    # 0-5  |  [NoRecord, TrackCrash, NormalClear, HardClear, UltimateChain, PerfectUltimateChain]
    #         [NO, CR, NC, HC, UC, PUC]
    # 6-16 |  [NO, D, C, B, A, A+, AA, AA+, AAA, AAA+, S]
    # 17   |  [sum]
    __level_table = np.load(local_dir + '/data/level_table.npy')
    for single_music in __level_table:  # Calculating the sum of each level
        if not single_music[0]:
            continue
        nov, adv, exh, inf, mxm = \
            int(single_music[10]), int(single_music[13]), int(single_music[16]), \
            int(single_music[19]), int(single_music[22])
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
        score, clear, grade, lv = record[3], record[4], record[5], int(record[8])
        level_summary[lv][clear_index[clear]] += 1
        level_summary[lv][grade_index[grade]] += 1
        hist_list[lv][int(grade_index[grade] - 11)].append(score // 10000)
        if lv >= lv_base and score > 8000000:
            violin_list.append([score, str(lv)])
    for index in range(21):
        level_summary[index][0] = level_summary[index][6] = level_summary[index][17] - sum(level_summary[index][1:6])
    violin_df = pd.DataFrame(violin_list, columns=['score', 'lv'])

    # Generate pure text message to return
    msg = '----------------Level Summary----------------\n' \
          'Level    NC      HC      UC      PUC     ||    AAA     AAA+    S       ||    SUM\n'
    for index in range(lv_base, 21):
        nc, hc, uc, puc = level_summary[index][2:6]
        aaa, aaa_plus, s, __sum = level_summary[index][14:]
        msg += ('lv.%d    ' % index)
        msg += ('%-8d%-8d%-8d%-8d||    %-8d%-8d%-8d||    %-8d\n' % (nc, hc, uc, puc, aaa, aaa_plus, s, __sum))
    timber.info('Generate summary data complete.\n\n%s\n' % msg)

    # Generate data frame for joint plot
    vf_list, vf_size, low_score, low_lv, high_lv = [], 100, 10000000, 20, 0  # Just [score: int, vf: float, lv: str]
    for record in music_map_sort[:vf_size]:
        if record[0]:
            score, lv, vf = record[3], record[8], record[10]
            vf_list.append((score, vf / 2, lv))
            low_score, low_lv, high_lv = min(low_score, score), min(low_lv, int(lv)), max(high_lv, int(lv))
    high_vf, low_vf = vf_list[0][1], vf_list[-1][1]
    vf_df = pd.DataFrame(vf_list, columns=['score', 'vf', 'lv'])

    try:  # If the plot module breaks down somehow, the function will try to return the pure text data.
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
        horizon = cv2.imread(img_archive + '/bg/bg_horizon.png', cv2.IMREAD_UNCHANGED) * 2
        horizon = np.repeat(horizon, 2, axis=0)

        # matplotlib & seaborn format config
        mat_font = FontProperties(fname=font_DFHS, size=12)
        sns.set_context("notebook")
        sns.set_style(style='darkgrid')
        sns.set_style(rc={
            'xtick.color': 'w',
            'ytick.color': 'w',
            'axes.labelcolor': 'w',
            'font.family': ['DejaVu Sans']
        })

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
        profile_field = Anchor(bg, 'profile field', free=(0, 0), father=prologue)
        std_profile = generate_std_profile(profile, vol_force)
        profile_x = std_profile.shape[1]
        profile_anc = AnchorImage(bg, 'profile image', std_profile, (30, (x_px - profile_x) // 2), profile_field)
        profile_anc.plot()

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

        title_font = ImageFont.truetype(font_continuum, 28, encoding='utf-8')
        title_text_anc = AnchorText(bg, 'title level', '', pen, title_font, (4, 52), title_anc)
        sub_font = ImageFont.truetype(font_DFHS, 22, encoding='utf-8', index=0)
        subtitle_text_anc = AnchorText(bg, 'subtitle', '', pen, sub_font, (14, 16), subtitle_anc)

        icon_bg = cv2.imread(img_archive + '/ms_sel/box_medal.png', cv2.IMREAD_UNCHANGED)
        icon_bg = cv2.resize(icon_bg, dsize=None, fx=box_ref, fy=box_ref, interpolation=cv2.INTER_AREA)
        glow_radius = 20
        icon_glow = outer_glow(icon_bg, color_l_blue, glow_radius)
        glow_anc = AnchorImage(bg, 'icon glow', icon_glow, free=(-glow_radius, -glow_radius))

        plot_bg_margin = 150
        plot_bg_glow = {'expand': 1, 'color': (0, 0, 0), 'radius': 7, 'opacity': 0.6}
        plot_bg_s_height, plot_bg_b_height = 500, 735

        plot_bg_s_size = (plot_bg_s_height, x_px - 2 * plot_bg_margin)
        plot_bg_s = generate_line_box(plot_bg_s_size, color_l_blue, (40, 59, 79), 2, 0.5,
                                      glow=plot_bg_glow, bg_img=horizon)
        plot_bg_s_anc = AnchorImage(bg, 'pie bg', plot_bg_s,
                                    (20 - plot_bg_glow['radius'], plot_bg_margin - plot_bg_glow['radius']))

        plot_bg_b_size = (plot_bg_b_height, x_px - 2 * plot_bg_margin)
        plot_bg_b = generate_line_box(plot_bg_b_size, color_l_blue, (40, 59, 78), 2, 0.5,
                                      glow=plot_bg_glow, bg_img=horizon)
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
                    AnchorText(bg, '%s text_b %d' % (name, __index), '', pen, sta_b_font, (7, text_shift), text_grid)
                text_b[__index].set_grid(grid_id)
                text_s[__index] = \
                    AnchorText(bg, '%s text_s %d' % (name, __index), '', pen, sta_s_font, (50, text_shift), text_grid)
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

        def plot_pie(data_list: list, color_tuple: tuple, legend: tuple, legend_loc: tuple,
                     size: tuple, l_col: int = 1):
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

            patch = plt.pie(np.ones(len(color_tuple), dtype=int), radius=0.01, colors=color_tuple)[0]
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

            sum_anc = AnchorText(bg, 'sum lv.%d' % lv_cur, '/%d' % lv_sum, pen, sta_b_font,
                                 (320, x_px // 2), content_field)
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
            try:  # Nothing to plot
                clear_pie_anc = AnchorImage(bg, 'clear_pie', clear_pie, free=(-40, 140), father=pie_field)
                clear_pie_anc.plot()
            except AttributeError:
                pass

            grade_pie = plot_pie(grade_data, grade_palette, grade_legend, (-0.1, -0.43), pie_size, l_col=3)
            grade_pie = get_matplotlib(grade_pie)
            try:
                grade_pie_anc = AnchorImage(bg, 'grade_pie', grade_pie, (-200, 520), father=pie_field)
                grade_pie_anc.plot()
            except AttributeError:
                pass

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
            try:  # Still nothing to do
                hist = plot_histogram(hist_data, hist_size, grade_legend[-6:], grade_palette[-6:])
                hist = get_matplotlib(hist)
                hist_anc = AnchorImage(bg, 'histogram', hist, (50, 150), father=hist_plot_field)
                hist_anc.plot()
            except ValueError:
                pass

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

        lv_range = high_lv - low_lv
        if lv_range < 6:
            joint_palette = level_palette[-lv_range - 1:]
        else:
            joint_palette = None

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
        joint = plot_joint(vf_df, joint_size, joint_palette)
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
        yeast_anc = AnchorText(bg, 'yea', 'Generated by Saccharomyces cerevisiae', pen, finale_font, (0, 0), finale_anc)
        author_anc = AnchorText(bg, 'author', 'Powered by Nyanm & Achernar', pen, finale_font, (30, 0), finale_anc)
        yeast_anc.plot(color_gray, pos='c')
        author_anc.plot(color_gray, pos='c')

        text_layer = np.array(text_layer)
        png_superimpose(bg, text_layer)
        output_path = '%s/%s_SUMMARY.png' % (cfg.output, validate_filename(user_name))
        cv2.imwrite(output_path, bg[:, :, :3], params=[cv2.IMWRITE_PNG_COMPRESSION, 3])

        try:
            remove(local_dir + '/data/matplotlib.png')
        except FileNotFoundError:
            pass

        timber.info_show('Plot saved at [%s] successfully.' % output_path)
        return msg

    except Exception:
        timber.warning('Something wrong happens in the plot function, only will the text message be returned.\n\n%s\n'
                       % format_exc())
        return msg
