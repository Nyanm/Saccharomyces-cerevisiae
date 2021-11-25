from .data import *

dependency = {
    "version": ['6'],

    'is_ifs': True,
    'ifs06': [
        'shutter',
        'psd_skill',
        'psd_num',
        'psd_level',
        'psd_crew',
        'play_data',
        'play_data_small',
        'ms_sel',
        'force',
        'ap_floor'
    ],

    'is_b64': True,
    'b64': [
        'bar',
        'bg',
        'font',
        'frame',
        'skill'
    ],
    'b64_bar': [
        [name_bar, 'name_bar.png'],
        [name_left, 'name_left.png'],
        [name_right, 'name_right.png'],
        [title_bar, 'title_bar.png'],
        [title_bg, 'title_bg.png'],
        [title_left, 'title_left.png'],
        [title_right, 'title_right.png']
    ],
    'b64_bg': [
        [box_semi, 'box_semi.png'],
        [bg_hex, 'bg_hex.png'],
        [bg_horizon, 'bg_horizon.png']
    ],
    'b64_font': [
        [DFHSMaruGothic_W4_reform, 'DFHSMaruGothic_W4_reform.ttf'],
        [unispace_bd, 'unispace_bd.ttf']
    ],
    'b64_frame': [
        [bar, 'bar.png'],
        [btm_left, 'btm_left.png'],
        [btm_orange, 'btm_orange.png'],
        [btm_right, 'btm_right.png'],
        [top_left, 'top_left.png'],
        [top_orange, 'top_orange.png'],
        [top_right, 'top_right.png']
    ],
    'b64_skill': [
        [skill_00, 'skill_00.png'],
        [skill_01, 'skill_01.png'],
        [skill_02, 'skill_02.png'],
        [skill_03, 'skill_03.png'],
        [skill_04, 'skill_04.png'],
        [skill_05, 'skill_05.png'],
        [skill_06, 'skill_06.png'],
        [skill_07, 'skill_07.png'],
        [skill_08, 'skill_08.png'],
        [skill_09, 'skill_09.png'],
        [skill_10, 'skill_10.png'],
        [skill_11, 'skill_11.png'],
        [skill_12, 'skill_12.png']
    ],

    'is_transport': True,
    'transport': ['continuum_medium.ttf'],
    'transport_continuum_medium.ttf': ['/graphics/font/0001', '/font/continuum_medium.ttf']
}
