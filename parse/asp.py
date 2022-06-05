import json

from util.logger import timber
from util.struct import MusicRecord, BestPtr
from util.cfg import Config

from value.mapping import clear_factor, grade_factor, crew_id


class AspParser:
    """
    TODO: ADD A BRIEF
    """

    def __init__(self, cfg: Config, map_size: int):
        # public zone
        # general music map
        self.musicRecordMap = [MusicRecord() for _ in range(map_size * + 1)]
        self.lastIndex: int = 0
        # user profile
        self.userName: str = ''
        self.apCard: int = 6001  # gen6 default appeal card
        self.akaName: str = 'よろしくお願いします'  # default name id=1
        self.skill: int = 0  # no skill
        self.crewID: str = '0014'  # Gen 6 Rasis
        # b50 data
        self.b50VF: int = 0
        self.bestMap = [BestPtr() for _ in range(100)]

        # load sdvx@asphyxia.db the json file
        raw_data = open(cfg.dbPath, 'r')
        last_time, skill_time, profile_time, crew_time = 0, 0, 0, 0  # records the last appearance time
        aka_index = 0  # index of akaName in music.db
        crew_index = 0  # index of crew in mapping.crew_id
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
            if cur_id != cfg.cardNum:
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

                self.musicRecordMap[cur_index].isRecorded = True
                self.musicRecordMap[cur_index].mID = mid
                self.musicRecordMap[cur_index].musicType = m_type
                self.musicRecordMap[cur_index].score = score
                self.musicRecordMap[cur_index].clear = clear
                self.musicRecordMap[cur_index].grade = grade
                self.musicRecordMap[cur_index].timestamp = m_time
                self.musicRecordMap[cur_index].exScore = exscore

                if m_time > last_time:
                    last_time = m_time
                    self.lastIndex = cur_index

            # profile record, contains username, appeal card, aka name
            elif line_type == 'profile':
                if cur_time > profile_time:
                    profile_time = cur_time
                    self.userName = json_dict['name']
                    self.apCard = json_dict['appeal']
                    aka_index = json_dict['akaname']

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
                        crew_index = json_dict['param'][24]

        if not self.lastIndex:  # no record found
            timber.error('Music record not found, make sure you have at least played once (and saved successfully). '
                         'Or you might check whether your card number has filled appropriately.')
            input('Press enter to continue.')
            exit(1)



















