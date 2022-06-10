# Dictionary for vf calculation
clear_factor = {0: 0, 1: 50, 2: 100, 3: 102, 4: 105, 5: 110}
grade_factor = {0: 0, 1: 80, 2: 82, 3: 85, 4: 88, 5: 91, 6: 94, 7: 97, 8: 100, 9: 102, 10: 105}

# Dictionary for score list
score_table = {
    'D': (0, 6499999),
    'C': (6500000, 7499999),
    'B': (7500000, 8699999),
    'A': (8700000, 8999999),
    'A+': (9000000, 9299999),
    'AA': (9300000, 9499999),
    'AA+': (9500000, 9699999),
    'AAA': (9700000, 9799999),
    'AAA+': (9800000, 9899999),
    'S': (9900000, 10000000)
}

# Look up table for crew, only support crew with LIVE-2D
crew_id = {
    116: '0001',  # gen5 grace (グレイス)
    95: '0002',   # gen5 rasis (レイシス)
    96: '0003',   # gen5 kureha (紅刃)
    100: '0004',  # gen5 reimu (博麗 霊夢)
    101: '0005',  # gen5 right (嬬武器 雷刀)
    102: '0006',  # gen5 grace-yukata (グレイス-浴衣)
    103: '0007',  # gen5 near & noah (ニア & ノア)
    104: '0008',  # gen5 nana (虹霓・シエル・奈奈)
    105: '0009',  # gen5 left (嬬武器烈風刀)
    106: '0010',  # gen5 natsuhi (夏陽)
    107: '0011',  # gen5 cocona (心菜)
    109: '0012',  # 09th kac 666 kureha
    112: '0013',  # gen5 konoha (恋刃)
    113: '0014',  # gen6 rasis (レイシス)
    117: '0015',  # gen6 grace (グレイス)
    118: '0016',  # gen6 april-fool-grace
    119: '0017',  # gen6 tsumabuki (つまぶき)
    120: '0018',  # gen6 near & noah (ニア & ノア)
    121: '0019',  # gen6 cawol & ashita (カヲル&アシタ)
    124: '0022',  # gen6 hiyuki-chan (氷雪ちゃん)
    128: '0023',  # 10th kac chrono-capsule rasis
}
