import json
import sys

from logger import timber
from utli import sheet


class ASPParser:
    def __init__(self, db_dir: str, map_size: int, card_num: str, aka_db):

        # load sdvx@asphyxia.db
        raw_data = open(db_dir, 'r')
        self.music_map = [[False, 0, 0, 0, 0, 0, 0, 0] for _ in range(map_size * 5 + 1)]
        """music_map is a comprehensive map to store player's play record
        It contains 5-time of map_size lines, each 5 lines define the 5 difficulties of a single song
        Each line of music map should be:
        [
            0: is_recorded(bool), 
            1: mid(int), 
            2: music_type(int), 
            3: score(int), 
            4: clear(int), 
            5: grade(int), 
            6: timestamp(int), 
            7: exscore(int),
        ]
        """

        self.skill, self.last_index, last_time = 0, 0, 0
        skill_time, profile_time, crew_time = 0, 0, 0
        for line in raw_data:
            json_dict = json.loads(line)

            # some lines have no collection name, pass them
            try:
                line_type = json_dict['collection']
            except KeyError:
                continue

            # some lines have no refid or timestamp, pass them anyway
            try:
                cur_id = json_dict['__refid']
                cur_time = json_dict['updatedAt']['$$date']
            except KeyError:
                continue

            # Specify user
            if cur_id != card_num:
                continue

            # music record, contains everything about this play
            if line_type == 'music':

                mid, m_type, score = json_dict['mid'], json_dict['type'], json_dict['score']
                clear, grade = json_dict['clear'], json_dict['grade']
                m_time = cur_time

                try:
                    exscore = json_dict['exscore']
                except KeyError:
                    exscore = 0

                cur_index = mid * 5 + m_type
                self.music_map[cur_index] = [True, mid, m_type, score, clear, grade, m_time, exscore]

                if m_type > last_time:
                    last_time = m_time
                    self.last_index = cur_index

            # profile record, contains username, appeal card, aka name
            elif line_type == 'profile':
                if cur_time > profile_time:
                    profile_time = cur_time
                    self.user_name, self.ap_card, self.aka_index = \
                        json_dict['name'], json_dict['appeal'], json_dict['akaname']

            # skill record, maintains highest skill you've achieved
            elif line_type == 'skill':
                if cur_time > skill_time:
                    skill_time = cur_time
                    self.skill = max(json_dict['base'], self.skill)

            # param record, use a uncanny way to store the crew
            elif line_type == 'param':
                if json_dict['type'] == 2 and json_dict['id'] == 1:
                    if cur_time > crew_time:
                        crew_time = cur_time
                        self._crew_index = json_dict['param'][24]

        if not self.last_index:
            timber.error('Music record not found, make sure you have at least played once (and saved successfully).')
            sys.exit(1)

        try:
            self.akaname = 'よろしくお願いします'  # If you have modified your aka name
            for akaname in aka_db:
                if int(akaname[0]) == self.aka_index:
                    self.akaname = akaname[1]
                    break
            try:
                self.crew_id = sheet.crew_id[self._crew_index]
            except KeyError:
                self.crew_id = '0014'  # Gen 6 Rasis

            timber.info('Profile data load successfully.\n'
                        'user name   :%s\nappeal card :%d\nakaname     :%s\nskill       :%d\ncrew        :%s\n' %
                        (self.user_name, self.ap_card, self.akaname, self.skill, self.crew_id))
        except AttributeError:
            timber.error('Profile/Skill/Crew data not found, '
                         'make sure you have at least played once (and saved successfully).')
            sys.exit(1)

        self.profile = [self.user_name, self.ap_card, self.akaname, self.skill, self.crew_id]
        timber.info('Asphyxia database parse complete.')
