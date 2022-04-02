# non-local packages
import os
import re
import sys
import time

# interior packages
from utli.cfg_read import cfg
from utli.logger import timber

# exterior packages
from utli import draft, sheet
from genre import packet
from parse import asp, npdb

VERSION = [1, 2, 'alpha']


class SDVX:

    def __init__(self):

        # Load skin
        try:
            self.plot_skin = packet[cfg.skin_name]
        except KeyError:
            timber.error('Invalid skin name, please check your configurations.')
            sys.exit(1)

    def _get_b50(self):
        b50_text = self.plot_skin.plot_b50(self.music_map.copy(), self.profile)
        input('%s\nPress enter to continue.' % b50_text)

    def _get_summary(self, base_lv: int):
        summary_text = self.plot_skin.plot_summary(self.music_map.copy(), self.profile, base_lv)
        input('%s\nPress enter to continue.' % summary_text)

    def _get_single(self, sg_index: int):
        sg_text = self.plot_skin.plot_single(self.music_map.copy(), self.profile, sg_index)
        input('%s\nPress enter to continue.' % sg_text)

    def _get_level(self, level: int, limits: tuple, grade_flag: str):
        level_text = self.plot_skin.plot_level(self.music_map, self.profile, level, limits, grade_flag)
        input('%s\nPress enter to continue.' % level_text)

    def _1_get_b50(self):
        os.system('cls')
        self._get_b50()

    def _2_get_summary(self):
        os.system('cls')
        base_lv = input(draft.TwoGetSummary.init_hint())
        timber.info('Get summary from level "%s"' % base_lv)

        if not base_lv:
            self._get_summary(17)
            return

        try:
            base_lv = int(base_lv)
            if base_lv > 20 or base_lv < 1:
                timber.warning('Invalid level number.')
                return
        except ValueError:
            timber.warning('Invalid level number.')
            return

        self._get_summary(base_lv)

    def _3_get_recent(self):
        print(draft.ThreeGetRecent.init_hint())
        __music_map = self.music_map.copy()
        __music_map.sort(key=lambda x: x[6])
        latest = __music_map[-1]
        self._get_single(latest[1] * 5 + latest[2])

    def _4_get_specific(self):

        def not_found_handler():
            timber.info('Record not found.')
            input(draft.FourGetSpecific.not_found())

        sg_index = 0
        sep_arg = input(draft.FourGetSpecific.init_hint()).split()
        timber.info('Get specific "%s"' % ' '.join(sep_arg))

        if len(sep_arg) == 1:  # Default highest difficulty
            try:
                mid = int(sep_arg[0])
                if mid > cfg.map_size:
                    not_found_handler()
                    return
            except ValueError:
                timber.warning('Invalid character was found, please try again and enter only number(s).\n'
                               'Press enter to continue.')
                return
            for lv_index in range(4, -1, -1):
                index = mid * 5 + lv_index
                if self.music_map[index][0]:
                    sg_index = index
                    break

        elif len(sep_arg) == 2:  # Stipulated difficulty
            try:
                mid, m_type = int(sep_arg[0]), int(sep_arg[1])
                if mid > cfg.map_size:
                    not_found_handler()
                    return
            except ValueError:
                timber.warning('Invalid character was found, please try again and enter only number(s).\n'
                               'Press enter to continue.')
                return
            if m_type >= 4:  # 4th difficulty
                mxm_index = mid * 5 + m_type
                inf_index = mid * 5 + m_type - 1
                if self.music_map[mxm_index][0]:
                    sg_index = mxm_index
                elif self.music_map[inf_index][0]:
                    sg_index = inf_index

            elif m_type > 0:  # 1st ~ 3rd difficulty
                index = mid * 5 + m_type - 1
                if self.music_map[index][0]:
                    sg_index = index

        else:
            timber.warning('Enter operators no more than 2. Press enter to continue.\n')
            return

        if not sg_index:
            not_found_handler()
            return

        print(draft.FourGetSpecific.search_res(sep_arg))
        self._get_single(sg_index)

    def _5_get_level(self):
        os.system('cls')
        level = input(draft.FiveGetLevel.init_hint())
        timber.info('Level "%s"' % level)
        try:
            level = int(level)
            if level > 20 or level < 1:
                timber.warning('Invalid level number. Please enter a positive number no more than 20.')
                return
        except ValueError:
            timber.warning('Invalid input. Please enter a positive number no more than 20.')
            return

        threshold = input(draft.FiveGetLevel.threshold()).upper().replace('P', '+')
        timber.info('Score limit %s' % threshold)

        if not threshold:  # entered nothing, default as querying all
            limits, grade_flag = (0, 10000000), 'ALL'
            print(draft.FiveGetLevel.all_songs(level))
        else:  # entered something, need further validity check
            try:
                # scores at a specific grade
                limits = sheet.score_table[threshold]
                grade_flag = threshold
            except KeyError:
                # scores between 2 limits

                # thou should enter only 2 numbers separated with '-'
                limits = threshold.split('-')
                if len(limits) != 2:
                    timber.warning('Invalid score. Please enter two positive numbers separated with "-".')
                    return

                try:  # thou should enter numbers between 0 and 10m
                    lim_1, lim_2 = int(limits[0]), int(limits[1])
                    if lim_1 > 10000000 or lim_1 < 0 or lim_2 > 10000000 or lim_2 < 0:
                        raise ValueError('')
                except ValueError:
                    timber.warning('Invalid input. Please enter two positive numbers no more than 10000000.')
                    return

                limits, grade_flag = (min(lim_1, lim_2), max(lim_1, lim_2)), None

            if grade_flag:
                print(draft.FiveGetLevel.grade_songs(level, grade_flag))
            else:
                print(draft.FiveGetLevel.limit_songs(level, limits[0], limits[1]))
        self._get_level(level, limits, grade_flag)

    def _8_search(self):
        os.system('cls')
        search_str = input(draft.EightSearch.init_hint())
        timber.info('Searching "%s"' % search_str)
        if search_str:

            result_list = []
            for index in range(1, cfg.map_size):
                try:
                    if re.search(search_str, self.search_db[index], re.I):
                        result_list.append(index)
                except re.error:
                    timber.info_clog('Invalid character (for regular expression) was entered, '
                                     'which crashed this query. Press enter to continue.')
                    return

            search_res = ('%d result(s) found:\n\n'
                          '|No  |MID   |Level        |Date        |Yomigana\n'
                          '     |Name  -  Artist\n\n' % len(result_list))
            for index in range(len(result_list)):
                __mid = result_list[index]
                __data = self.level_table[__mid]
                __date = '%s/%s/%s' % (__data[7][:4], __data[7][4:6], __data[7][6:])
                search_res += '|%-4d|%-4d  |%s/%s/%s/%s  |%-8s  |%s\n     |%s  -  %s\n\n' % \
                              (index + 1, __mid, __data[10].zfill(2), __data[13].zfill(2), __data[16].zfill(2),
                               str(int(__data[19]) + int(__data[22])).zfill(2), __date, __data[2], __data[1], __data[3])

            res_num = len(result_list)

            if res_num:
                timber.info(search_res)
                print(draft.EightSearch.success(res_num, search_res))
            else:
                print(draft.EightSearch.failed())
                timber.info('Search failed.')
        else:
            print(draft.EightSearch.empty())
        input(draft.CommonMsg.enter())

    def _9_faq(self):
        os.system('cls')
        timber.info('FAQ')
        print(draft.NineFAQ.first(self.user_name))
        print(draft.NineFAQ.second())
        input(draft.CommonMsg.enter())

    def _0_see_you_next_time(self):
        timber.info('Exit by operator number 0.')
        print(draft.ZeroExit.farewell(self.user_name))
        time.sleep(1.5)
        sys.exit(0)

    @staticmethod
    def _10_donate():
        os.system('cls')
        timber.info('Ali-pay is also recommended.')
        print(draft.TenDonate.init_hint())
        input(draft.TenDonate.back_to_light())

    def input_handler(self):
        key_dict = {
            '1': self._1_get_b50,
            '2': self._2_get_summary,
            '3': self._3_get_recent,
            '4': self._4_get_specific,
            '5': self._5_get_level,
            '8': self._8_search,
            '9': self._9_faq,
            '0': self._0_see_you_next_time,
            '10': self._10_donate
        }

        os.system('cls')
        time.sleep(0.05)
        print(draft.TitleMsg.title(VERSION), end='')
        while True:
            base_arg = input()
            timber.info('Get user operator %s' % base_arg)
            try:
                key_dict[base_arg]()
                break
            except KeyError:
                pass


for line in npdb.level_table:
    print(line)
