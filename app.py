from util.cfg import Config

from parse.asp import AspParser
from parse.sdvx import SdvxParser


class Application:

    def __init__(self):

        self.cfg = Config()
        self.sdvxParser = SdvxParser(self.cfg)
        self.sdvxParser.mapSize = 2000
        self.aspParser = AspParser(cfg=self.cfg, map_size=self.sdvxParser.mapSize)
