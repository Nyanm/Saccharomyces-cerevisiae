from util.cfg import Config

from parse.asp import AspParser
from parse.sdvx import SdvxParser


class Application:

    def __init__(self):

        cfg = Config()
        sdvx_parser = SdvxParser(cfg)
        asp_parser = AspParser(cfg, sdvx_parser.mapSize)
