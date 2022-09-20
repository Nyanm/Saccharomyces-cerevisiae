from .cmd_def import CommandStruct


class CommandConsole:
    REGISTER_DUPLICATE_COMMAND = ''
    PARSE_UNKNOWN_COMMAND = ''
    PARSE_DUPLICATE_ARG = ''
    PARSE_UNKNOWN_ARG = ''

    def __init__(self):
        self._map_commands: dict = {}
        """{command_url: str -> command_entity: CommandStruct}"""
        self._map_commands_abbr: dict = {}
        """{command_url_abbr -> command_url: str}"""

    def register(self, command_entity: CommandStruct) -> bool:
        pass

    def _parse(self, raw: str, empty_param: dict) -> bool:
        raw_list = raw.split()

    def run(self):
        pass
