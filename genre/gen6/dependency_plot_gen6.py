from .data_plot_gen6 import *


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
        'ms_sel',
        'force',
        'cmn_window',
        'card_entry',
        'ap_floor'
    ],

    'is_b64': True,
    'b64': [
        'bar',
        'bg',
        'font',
        'frame',
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
        [top_right, 'top_right.png']],

    'is_transport': True,
    'transport': ['commaexr.ttf'],
    'transport_commaexr.ttf': ['/graphics/font/commaexr.ttf', 'font']
}