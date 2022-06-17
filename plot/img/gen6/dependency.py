from .b64_data import *

dependency = {

    # basic info
    'skin_name': 'gen6',

    # ifs filed
    'is_ifs': True,
    'ifs_ver': [6],
    'ifs_06': [
        'shutter',
        'psd_skill',
        'psd_num',
        'psd_level',
        'psd_crew',
        'play_data',
        'play_data_small',
        'ms_sel',
        'force',
        'ap_floor',
    ],

    # b64 field
    'is_b64': True,
    'b64': [
        'skill',
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

    # transport field
    'is_tsp': True,
    'tsp': ['MaruGothicBD', 'ContinuumMD'],
    'tsp_MaruGothicBD': ['/data//graphics/font/0000', '/font/DFMaruGothic-Bd.ttf'],
    'tsp_ContinuumMD': ['/data/graphics/font/0001', '/font/continuum_medium.ttf'],
}
