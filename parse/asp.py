import json
import heapq

from util.logger import timber
from util.struct import MusicRecord
from util.cfg import Config

import value.mapping as val_map
from value.project_cfg import BEST_MAP_SIZE


class AspParser:
    """
    TODO: ADD A BRIEF
    """

    def __init__(self, cfg: Config, map_size: int):
        # public zone
        # general music map
        self.musicRecordMap = [MusicRecord() for _ in range(map_size * 5 + 1)]
        self.lastIndex: int = 0
        # user profile
        self.userName: str = ''
        self.apCard: int = 6001  # gen6 default appeal card
        self.akaName: str = 'よろしくお願いします'  # default name id=1
        self.skill: int = 0  # no skill
        self.crewID: str = '0014'  # Gen 6 Rasis
        # b50 data
        self.b50VF: int = 0
        self.bestMap = []

        # load sdvx@asphyxia.db the json file
        raw_data = open(cfg.dbPath, 'r')
        last_time, skill_time, profile_time, crew_time = 0, 0, 0, 0  # records the last appearance time
        self._aka_index = 0  # index of akaName in music.db, lookup in SdvxParser.akaDataMap
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
                    self._aka_index = json_dict['akaname']

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

        # (try to) update crewID
        try:
            self.crewID = val_map.crew_id[crew_index]
            timber.debug(f'crew id (index={crew_index}) updated to {self.crewID}.')
        except KeyError:
            timber.debug(f'crew id (index={crew_index}) not found, the program will keep the default crew Gen 6 Rasis. '
                         f'Everyone loves Rasis.')

    def update_aka(self, aka_data_map: list):
        for aka_data in aka_data_map:
            if self._aka_index == aka_data.akaID:
                self.akaName = aka_data.akaName
                timber.debug(f'aka name (index={self._aka_index}) updated to {self.akaName}.')
                return
        timber.debug(f'aka name (index={self._aka_index}) not found. You may have costumed your akaname before.')

    def update_lv_vf(self, music_data_map: list):
        """
        Copied from BEMANI WIKI 2ND:

        VOLFORCE計算方法
        単曲FORCE計算式：Lv×(スコア÷1000万)×(GRADE係数)×(クリアメダル係数)×2(小数第1位まで算出し、以降切り捨て)
        VOLFORCE計算式:VOLFORCE対象曲の単曲FORCE(50譜面)の合計÷100
        """
        for _record in self.musicRecordMap:
            if not _record.isRecorded:
                continue
            _data = music_data_map[_record.mID]
            levels = [_data.novice.level, _data.advanced.level, _data.exhausted.level,
                      _data.infinite.level, _data.maximum.level]
            clear_factor = val_map.clear_factor[_record.clear]
            grade_factor = val_map.grade_factor[_record.grade]
            level = levels[_record.musicType]
            score = _record.score
            vf = level * score * clear_factor * grade_factor # vf is an integer

            _record.level = level
            _record.vf = vf

            if len(self.bestMap) < BEST_MAP_SIZE:  # the heap still has spare space
                heapq.heappush(self.bestMap, _record)
            else:  # gotta kick someone out
                if vf > self.bestMap[0].vf:  # kick it!
                    heapq.heappop(self.bestMap)
                    heapq.heappush(self.bestMap, _record)

        # sort them by vf
        self.bestMap.sort(key=lambda record: record.vf, reverse=True)
        # get b50 the value
        for index in range(50):
            try:
                self.b50VF += self.bestMap[index].vf * 2 // 1000000
            except IndexError:
                timber.debug(f'Only {index} records were found, try to play more next time.')
                break
        self.b50VF /= 1000
        timber.debug(f'Calculate B50 VolForce {self.b50VF}')

    @property
    def profile(self):
        return self.userName, self.apCard, self.akaName, self.skill, self.crewID
