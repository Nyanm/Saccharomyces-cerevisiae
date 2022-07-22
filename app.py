from util.cfg import Config

from parse.asp import AspParser
from parse.sdvx import SdvxParser

from plot.handler.update import update_images
from plot.img.gen6.dependency import dependency


class Application:
    """
    TODO: THIS SHOULD BE A BRIEF :(
    """

    def __init__(self):
        self.cfg = Config()
        self.sdvxParser = SdvxParser(cfg=self.cfg)
        self.aspParser = AspParser(cfg=self.cfg, map_size=self.sdvxParser.mapSize)
        self.aspParser.update_lv_vf(music_data_map=self.sdvxParser.musicDataMap)
        self.aspParser.update_aka(aka_data_map=self.sdvxParser.akaDataMap)

    def run(self):
        pass
