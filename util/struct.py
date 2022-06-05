class MusicData:

    def __init__(self):
        self.mID: int = 0

        self.name: str = ''
        self.nameYmgn: str = ''  # ymgn = 読み仮名
        self.artist: str = ''
        self.artistYmgn: str = ''

        self.bpmMax: int = 0
        self.bpmMin: int = 0
        self.date: int = 0
        self.version: int = 0
        self.infVer: int = 0

        # difficult field
        self.novice: LevelData = LevelData()
        self.advanced: LevelData = LevelData()
        self.exhausted: LevelData = LevelData()
        self.infinite: LevelData = LevelData()
        self.maximum: LevelData = LevelData()


class LevelData:

    def __init__(self):
        self.level: int = 0
        self.illustrator: str = 'dummy'
        self.effector: str = 'dummy'
        # radar map values
        self.notes: int = 0
        self.peak: int = 0
        self.tsumami: int = 0
        self.tricky: int = 0
        self.handTrip: int = 0
        self.oneHand: int = 0


class AkaData:

    def __init__(self):
        self.mID: int = 0
        self.akaName: str = ''


class SearchData:

    def __init__(self):
        self.mID: int = 0
        self.meme: str = ''


class MusicRecord:

    def __init__(self):
        self.isRecorded: bool = False
        self.mID: int = 0
        self.musicType: int = 0
        self.score: int = 0
        self.clear: int = 0
        self.grade: int = 0
        self.timestamp: int = 0
        self.exScore: int = 0
        # non-native values
        self.level: int = 0
        self.vf: int = 0


class BestPtr:

    def __init__(self):
        self.vf: int = 0
        self.mID: int = 0

    def __gt__(self, other):
        return self.vf > other.vf
