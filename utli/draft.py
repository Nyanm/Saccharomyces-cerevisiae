from functools import wraps
import base64
import qrcode

from utli.cfg_read import cfg

LAN = cfg.language
DFT_LAN = 'EN'
uncanny_b64 = 'aHR0cHM6Ly92ZHNlLmJkc3RhdGljLmNvbS8vMTkyZDlhOThkNzgyZDljNzRjOTZmMDlkYjkzNzhkOTMubXA0'


def _languageHandler(func):
    """
    Call template:

    @staticmethod
    @_languageHandler
    def _() -> tuple:
        msg = {
            'EN': '',
            'ZH': '',
        }
        return msg,
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        msg_tuple, msg_list = func(*args, **kwargs), []
        for index in range(len(msg_tuple)):
            if msg_tuple[index].get(LAN):
                msg_list.append(msg_tuple[index].get(LAN))
            else:
                msg_list.append(msg_tuple[index].get(DFT_LAN))
        return ''.join(msg_list)

    return wrapper


class CommonMsg:
    @staticmethod
    @_languageHandler
    def enter() -> tuple:
        msg = {
            'EN': 'Press enter to continue.',
            'ZH': '按回车继续。',
        }
        return msg,


class TitleMsg:

    # pyfiglet conflict with pyinstaller, so I have no choice but spell it by my own :(
    @staticmethod
    @_languageHandler
    def title(ver_list: list) -> tuple:
        logo = {
            'EN': " ____                 _                                                   \n"
                  "/ ___|  __ _  ___ ___| |__   __ _ _ __ ___  _ __ ___  _   _  ___ ___  ___ \n"
                  "\___ \ / _` |/ __/ __| '_ \ / _` | '__/ _ \| '_ ` _ \| | | |/ __/ _ \/ __|\n"
                  " ___) | (_| | (_| (__| | | | (_| | | | (_) | | | | | | |_| | (_|  __/\__ \\\n"
                  "|____/ \__,_|\___\___|_| |_|\__,_|_|  \___/|_| |_| |_|\__, |\___\___||___/\n"
                  "                                                      |___/               \n"
                  "                                       _     _            \n"
                  "                ___ ___ _ __ _____   _(_)___(_) __ _  ___ \n"
                  "               / __/ _ \ '__/ _ \ \ / / / __| |/ _` |/ _ \\\n"
                  "              | (_|  __/ | |  __/\ V /| \__ \ | (_| |  __/\n"
                  "               \___\___|_|  \___| \_/ |_|___/_|\__,_|\___|\n"
                  "\n"
                  "                    Simple SDVX@Asphyxia Score Checker                    \n"
                  "                              Version %s\n"
                  "                       Powered by Nyanm & Achernar\n"
                  "\n" % '.'.join(map(str, ver_list))
        }
        menu = {
            'EN': "Score checker function field\n"
                  "[1] Best 50 Songs query                 [2] User summary        \n"
                  "[3] Recent play record                  [4] Specific song record\n"
                  "[5] Score list\n"
                  "\n"
                  "Common function field\n"
                  "[8] Search mid                          [9] FAQ\n"
                  "[0] Exit\n"
                  "\n"
                  "Enter corresponding number to continue:",

            'ZH': "查分器功能\n"
                  "[1] B50成绩查询                          [2] 玩家点灯总结\n"
                  "[3] 最近游玩记录                         [4] 特定歌曲记录\n"
                  "[5] 歌曲分数列表\n"
                  "\n"
                  "通常功能\n"
                  "[8] 搜索歌曲mid                          [9] 常见问题\n"
                  "[0] 退出\n"
                  "\n"
                  "输入相应数字后回车以继续:",
        }
        return logo, menu,


class TwoGetSummary:
    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        msg = {
            'EN': 'This function will generate summaries form lv.base to lv.20. \n'
                  'Please enter the lv.base you want, default as 17:',
            'ZH': '该功能将生成 等级下限 - lv.20 的摘要\n请输入等级下限，默认为17:',
        }
        return msg,


class ThreeGetRecent:
    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        msg = {
            'EN': '\nRecent play record:',
            'ZH': '\n最近游玩记录:',
        }
        return msg,


class FourGetSpecific:

    @staticmethod
    @_languageHandler
    def not_found() -> tuple:
        msg = {
            'EN': 'Record not found. Press enter to continue.',
            'ZH': '未查询到记录，按回车继续',
        }
        return msg,

    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        diff = {
            'EN': '\nNOV->1   ADV->2   EXH->3   INF/GRV/HVN/VVD/MXM->4\n'
        }
        msg = {
            'EN': 'Enter operators like "[mid] [diff(optional)], Search highest difficulty as default, \n'
                  'for example: Kyokuken -> 927 4 (or 927)"\n',
            'ZH': '输入指令形如[歌曲mid] [难度(可选)]，默认搜索最高难度，例如: 天极圈 -> 927 4 (或者 927)\n',
        }
        return diff, msg,

    @staticmethod
    @_languageHandler
    def search_res(sep_arg: list) -> tuple:
        msg = {
            'EN': '\nPlay record for "%s":' % ' '.join(sep_arg),
            'ZH': '\n"%s" 查询结果:' % ' '.join(sep_arg),
        }
        return msg,


class FiveGetLevel:
    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        msg = {
            'EN': 'Enter the level you want to query (1~20):',
            'ZH': '输入需要查询的歌曲等级:',
        }
        return msg,

    @staticmethod
    @_languageHandler
    def threshold() -> tuple:
        msg = {
            'EN': 'Enter the grade you want to query. Or you can stipulate the score ceiling and floor.\n'
                  'Examples:\n'
                  '|Input            |Translated score limit(inclusive)\n',
            'ZH': '输入查询的分数等级，或者指定所查的分数上下限。\n'
                  '例:'
                  '|输入             |分数区间(包含)\n',
        }
        example = {
            'EN': '|B                |7500000-8699999\n'
                  '|AA+              |9500000-9699999\n'
                  '|S                |9900000-10000000\n'
                  '|                 |      0-10000000\n'
                  '|9000000-9650000  |9000000-9650000\n\n',
        }
        return msg, example,

    @staticmethod
    @_languageHandler
    def all_songs(level: int) -> tuple:
        msg = {
            'EN': 'Score list for all level %d songs:\n' % level,
            'ZH': '等级 %d 下全部歌曲成绩:\n' % level,
        }
        return msg,

    @staticmethod
    @_languageHandler
    def grade_songs(level: int, grade_flag: str) -> tuple:
        msg = {
            'EN': 'Score list for level %d at grade %s:\n' % (level, grade_flag),
            'ZH': '等级 %d，评级 %s 下全部歌曲:\n' % (level, grade_flag),
        }
        return msg,

    @staticmethod
    @_languageHandler
    def limit_songs(level: int, low: int, high: int) -> tuple:
        msg = {
            'EN': 'Score list for level %d in %d - %d:\n' % (level, low, high),
            'ZH': '等级 %d，分数区间 %d - %d 下全部歌曲:' % (level, low, high),
        }
        return msg,


class EightSearch:

    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        msg = {
            'EN': 'Enter relative message(Name, Artist, Memes)about the song you want to search, not case-sensitive:\n',
            'ZH': '输入想要查询的歌曲的相关信息(曲名、作者或者梗)后回车，不区分大小写\n',
        }
        return msg,

    @staticmethod
    @_languageHandler
    def success(res_num: int, search_res: str) -> tuple:
        msg = {
            'EN': '\n%d results found  %s' % (res_num, search_res),
            'ZH': '\n共搜索到%d个结果  %s' % (res_num, search_res),
        }
        return msg,

    @staticmethod
    @_languageHandler
    def failed() -> tuple:
        msg = {
            'EN': '\nNo search result found',
            'ZH': '\n未能搜索到结果',
        }
        return msg,

    @staticmethod
    @_languageHandler
    def empty() -> tuple:
        msg = {
            'EN': 'Empty input. Please try again and at least enter something.',
            'ZH': '未输入任何内容，试着搜点什么吧',
        }
        return msg,


class NineFAQ:
    @staticmethod
    @_languageHandler
    def first(user_name: str) -> tuple:
        msg = {
            'EN': '[1] Is there any other skin?\n'
                  ' -  Apparently the only skin we have is the primary skin for Saccharomyces cerevisiae:[gen6] :(\n'
                  '    But you, %s, you can join us and help us to develop new skins!\n' % user_name,
            'ZH': '[1] 还有其他皮肤吗？\n'
                  ' -  显然这软件只有gen6一个默认皮肤:(\n'
                  '    但是%s，你可以加入我们来开发新的皮肤！\n' % user_name,
        }
        return msg,

    @staticmethod
    @_languageHandler
    def second() -> tuple:
        msg = {
            'EN': '[2] Where can I get the source code?\n'
                  ' -  https://github.com/Nyanm/Saccharomyces-cerevisiae, and welcome to star my project!\n'
                  '    Also, the up-to-date release will be uploaded here.\n',
            'ZH': '[2] 在哪里可以找到源码？\n'
                  ' -  https://github.com/Nyanm/Saccharomyces-cerevisiae，欢迎来给项目点星星！'
                  '    同时，最新的发行版本也会在这里发布。',
        }
        return msg,


class ZeroExit:
    @staticmethod
    @_languageHandler
    def farewell(user_name) -> tuple:
        msg = {
            'EN': '\nSee you next time, %s' % user_name,
        }
        return msg,


class TenDonate:
    @staticmethod
    @_languageHandler
    def init_hint() -> tuple:
        msg = {
            'EN': 'Congratulations! You\'ve found the dark side of the moon!\n'
                  'Here is a donate page, '
                  'where you can buy the developer a cup of coffee if you like this application.\n'
                  '↓↓↓   Wechat QrCode   ↓↓↓',
            'ZH': '恭喜你发现了月之暗面！这里是一个赞助页面，可以请开发者喝一杯咖啡~\n'
                  '↓↓↓   微信二维码   ↓↓↓\n',
        }

        def get_uncanny_qr_str() -> str:
            _msg = ''
            _qr = qrcode.QRCode()
            _qr.add_data(base64.b64decode(uncanny_b64))
            mat = _qr.get_matrix()
            for line in mat:
                for column in line:
                    if column:
                        _msg += '  '
                    else:
                        _msg += '██'
                _msg += '\n'
            return _msg

        qr = {
            'EN': get_uncanny_qr_str(),
        }
        return msg, qr,

    @staticmethod
    @_languageHandler
    def back_to_light() -> tuple:
        msg = {
            'EN': 'Press enter to return the light side.',
            'ZH': '按回车回到亚伊太利斯。',
        }
        return msg,
