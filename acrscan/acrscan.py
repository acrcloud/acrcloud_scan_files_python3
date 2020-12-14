#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import csv
import json
import sys
from typing import List

from retrying import retry

from .acrcloud.recognizer import ACRCloudRecognizer
from .acrcloud.recognizer import ACRCloudStatusCode
from .models import *
from .utils import *

logger = logging.getLogger(__name__)


class ACRCloudScan:

    def __init__(self, acrcloud_config: dict) -> None:
        self.config = acrcloud_config  # config
        self._recognizer = ACRCloudRecognizer(self.config)
        self._recognize_length_ms = 10 * 1000
        self.filter_title_threshold = 75
        self.filter_time_threshold = self._recognize_length_ms
        self.results_counter = {}
        self.scan_type = ScanType.SCAN_TYPE_BOTH
        self.with_duration = False
        self.filter_results = False
        self.split_results = False
        self.start_time_ms = 0 * 1000
        self.end_time_ms = None
        self.is_fingerprint = False
        self.fp_buffer = None

    def _get_file_duration_ms(self, filename: str) -> int:
        """
        get the file's total play duration
        :param filename: the file position
        :return: the duration of the file (int)
        """
        if self.is_fingerprint:
            return self._recognizer.get_duration_ms_by_fpbuffer(self.fp_buffer)
        else:
            return self._recognizer.get_duration_ms_by_file(filename)

    @retry(stop_max_attempt_number=5, wait_exponential_multiplier=1000, wait_exponential_max=2000)
    def _recognize(self, filename: str, start_time_ms: int) -> dict:
        """
        do recognize and deserialization the json
        :param filename: file position
        :param start_time_ms: start time
        :return: recognize result (dict)
        """

        recognize_length_s = int(self._recognize_length_ms / 1000)

        start_time_s = int(start_time_ms / 1000)
        if self.is_fingerprint:
            result = self._recognizer.recognize_by_fpbuffer(self.fp_buffer, start_time_s, recognize_length_s)
        else:
            result = self._recognizer.recognize_by_file(filename, start_time_s, recognize_length_s)
        logger.debug(str(result).strip())
        result = json.loads(result)
        if result.get('code') == 3000:
            raise Exception('Http Error"')
        return result

    def _scan(self, filename: str) -> (list, list):
        """
        scan a whole file.
        :param filename: filename
        :return: a list response (it will save as an attribute of a object)
        """
        music_results = []
        custom_file_results = []
        if self.is_fingerprint:
            with open(filename, 'rb') as f:
                self.fp_buffer = f.read()

        if self.end_time_ms:
            duration_ms = self.end_time_ms
        else:
            duration_ms = self._get_file_duration_ms(filename)

        if not duration_ms:
            duration_ms = 0

        duration_left_ms = duration_ms % self._recognize_length_ms

        # ignore extra fragment (if this fragment smaller than 2 seconds)
        if duration_left_ms < 2000:
            scan_duration_ms = duration_ms - duration_left_ms
        else:
            scan_duration_ms = duration_ms

        logger.info(
            f'{filename} File total duration {duration_ms / 1000} seconds, Scan from 0 to {scan_duration_ms / 1000}')

        for t_ms in range(self.start_time_ms, scan_duration_ms, self._recognize_length_ms):
            rec_result = self._recognize(filename, t_ms)
            logger.info("progress: {}/{}".format(t_ms, scan_duration_ms))
            response = Response.from_dict(rec_result)
            response_code = response.status.code
            if response_code != 1001 and response_code != 0 and response_code != 2006:
                logger.error(f'Code:{response_code} Message: {response.status.msg}')
                # sys.exit()
            if response_code == ACRCloudStatusCode.DECODE_ERROR_CODE:
                logger.error(f'Code:{response_code} Message: {response.status.msg}, skip file {filename}')
                break

            music_result, custom_file_result = self._parse_response_to_result(filename, t_ms, response)
            music_results.append(music_result)
            custom_file_results.append(custom_file_result)

            logger.info(f'From {get_human_readable_time(int(t_ms / 1000))} '
                        f'To {get_human_readable_time(int((t_ms + self._recognize_length_ms) / 1000))} '
                        f'Result[title: {music_result.title} '
                        f'Custom: {custom_file_result.title}]')

        return music_results, custom_file_results

    def _parse_response_to_result(self, filename: str, start_time_ms: int, response: Response) \
            -> (MusicResult, CustomFileResult):
        """
        parse the Response object to Result object
        :param filename: filename
        :param start_time_ms: recognize start
        :param response:
        :return:
        """
        # initial the result
        # if no result or other situation set the title to the ACRCloud msg and set the accuracy to 100%
        music_result = MusicResult(
            filename=os.path.basename(filename),
            status_code=response.status.code,
            start_time_ms=start_time_ms,
            end_time_ms=start_time_ms + self._recognize_length_ms,
            played_duration_ms=self._recognize_length_ms,
            score=0,
        )

        custom_file_result = CustomFileResult(
            filename=os.path.basename(filename),
            status_code=response.status.code,
            start_time_ms=start_time_ms,
            end_time_ms=start_time_ms + self._recognize_length_ms,
            played_duration_ms=self._recognize_length_ms,
            score=0,
        )

        if response.status.code == ACRCloudStatusCode.ACR_ERR_CODE_OK:

            # music
            music_results = response.metadata.music

            if music_results:
                primary_music_result = music_results[0]
                keys = primary_music_result.to_dict()

                for k in keys:
                    music_result.__setattr__(k, primary_music_result.__getattribute__(k))

                if primary_music_result.external_ids.isrc:
                    music_result.isrc = primary_music_result.external_ids.isrc
                if primary_music_result.external_ids.upc:
                    music_result.upc = primary_music_result.external_ids.upc
                if primary_music_result.external_metadata.spotify and \
                        primary_music_result.external_metadata.spotify.track:
                    music_result.spotify_id = primary_music_result.external_metadata.spotify.track.id
                if primary_music_result.external_metadata.youtube:
                    music_result.youtube_id = primary_music_result.external_metadata.youtube.vid
                if primary_music_result.external_metadata.deezer and \
                        primary_music_result.external_metadata.deezer.track:
                    music_result.deezer_id = primary_music_result.external_metadata.deezer.track.id
                if primary_music_result.release_date:
                    music_result.release_date = primary_music_result.release_date
                if primary_music_result.label:
                    music_result.label = primary_music_result.label

                if primary_music_result.language:
                    music_result.language = primary_music_result.language

                if primary_music_result.album.name:
                    music_result.album_name = primary_music_result.album.name

                if primary_music_result.contributors:
                    if primary_music_result.contributors.composers:
                        composers_names_list = []
                        for c in primary_music_result.contributors.composers:
                            composers_names_list.append(c)

                        composers_names = "|##|".join(composers_names_list)
                        music_result.composers = composers_names

                    if primary_music_result.contributors.lyricists:
                        lyricists_names_list = []
                        for k in primary_music_result.contributors.lyricists:
                            lyricists_names_list.append(k)
                        lyricists_names = "|##|".join(lyricists_names_list)
                        music_result.lyricists = lyricists_names

                if primary_music_result.lyrics and primary_music_result.lyrics.copyrights:
                    lyrics_copyrights_list = []
                    for ly in primary_music_result.lyrics.copyrights:
                        lyrics_copyrights_list.append(ly)
                    lyrics_copyrights = "|##|".join(lyrics_copyrights_list)
                    music_result.lyrics = lyrics_copyrights
                else:
                    music_result.lyrics = None

                if primary_music_result.artists:
                    artists_names_list = []
                    for a in primary_music_result.artists:
                        artists_names_list.append(a.name)

                    artists_names = "|##|".join(artists_names_list)
                    music_result.artists_names = artists_names

                similar_results = music_results[1:]
                music_result.similar_results = similar_results
                music_result.primary_result = primary_music_result

                if self.with_duration:
                    if music_result.sample_begin_time_offset_ms is None:
                        logger.error('Please contact us (support@acrcloud.com) to get the \'played duration\' feature '
                                     'permission')
                    else:
                        music_result.played_duration_ms = \
                            music_result.sample_end_time_offset_ms - music_result.sample_begin_time_offset_ms
                        music_result.db_begin_time_offset_ms = primary_music_result.db_begin_time_offset_ms
                        music_result.db_end_time_offset_ms = primary_music_result.db_end_time_offset_ms

            # custom file

            custom_files_results = response.metadata.custom_files

            if custom_files_results:

                primary_result = custom_files_results[0]

                keys = primary_result.to_dict()

                for k in keys:
                    custom_file_result.__setattr__(k, primary_result.__getattribute__(k))

                similar_results = custom_files_results[1:]
                custom_file_result.similar_results = similar_results
                custom_file_result.primary_result = primary_result

                if self.with_duration:
                    if custom_file_result.sample_begin_time_offset_ms is None:
                        logger.error('Please contact us (support@acrcloud.com) to get the \'played duration\' feature '
                                     'permission')
                    else:
                        custom_file_result.played_duration_ms = \
                            custom_file_result.sample_end_time_offset_ms - \
                            custom_file_result.sample_begin_time_offset_ms

        return music_result, custom_file_result

    def _compare_two_results(self, results, results_a_index: int, results_b_index: int) -> bool:
        """
        compare two results, determine which should be selected
        :param results_a_index:
        :param results_b_index:
        :return:
        """
        # first: compare the appear times
        results_a = results[results_a_index]
        results_b = results[results_b_index]
        results_a_count = self.results_counter[results_a.acrid].get('count')
        results_b_count = self.results_counter[results_b.acrid].get('count')
        if abs(results_a_count - results_b_count) > 1:
            if results_a_count > results_b_count:
                return True
            return False

        # second: compare the confidence score
        results_a_score_sum = self.results_counter[results_a.acrid].get('score_sum')
        results_b_score_sum = self.results_counter[results_b.acrid].get('score_sum')

        if abs(results_a_score_sum - results_b_score_sum) > 5:
            if results_a_score_sum > results_b_score_sum:
                return True
            return False

        # third:  compare the amount of the metadata.
        keys = results_a.to_dict()
        count_a_attr = len([i for i in keys if results_a.__getattribute__(i)])
        count_b_attr = len([i for i in keys if results_b.__getattribute__(i)])

        if count_a_attr >= count_b_attr:
            return True

        return False

    def _is_continuous(self, results, results_a_index: int, results_b_index: int) -> bool:
        """
        determine if two results are continuous
        :param results_a_index:
        :param results_b_index:
        :return:
        """

        results_a = results[results_a_index]
        results_b = results[results_b_index]

        results_m = results[results_a_index + 1]

        if results_a.db_end_time_offset_ms + results_m.played_duration_ms \
                - results_b.db_begin_time_offset_ms < self.filter_time_threshold:
            return True
        return False

    def _filter_results(self, results) -> List[MusicResult]:
        """
        deep filter (only can run after 'merge_results'
        :return: filtered results List[MusicResult]
        """
        # results = self.music_results
        self.results_counter = {}
        # count every single result
        for result in results:
            if result.status_code == ACRCloudStatusCode.ACR_ERR_CODE_OK:
                if not self.results_counter.get(result.acrid):
                    self.results_counter[result.acrid] = {
                        'count': 0,
                        'raw_result': result.primary_result,
                        'score_sum': 0
                    }

                self.results_counter[result.acrid]['count'] += 1
                self.results_counter[result.acrid]['score_sum'] += result.score

        index = 1
        # traverse the whole results list
        while True:
            if index >= len(results) - 1:
                break
            current_result = results[index]
            if current_result.status_code == ACRCloudStatusCode.NO_RESULT_CODE:
                # if face a no result record. use fuzzywuzzy to determine the previous and next titles are similar
                # because there are different versions of the same music in the database
                # e.g. Hello, Hello (Remix), Hello (feat. acr)

                if is_title_similar_or_equal(results[index - 1].title, results[index + 1].title,
                                             self.filter_title_threshold):
                    # if the title is the same, should consider the time should be increased
                    # previous_db_end_time + current_played_duration < next_start_time
                    # cause may have some error, so if the difference value < 10 seconds
                    # it should be considered continuous
                    if self._is_continuous(results, index - 1, index + 1):
                        # Because different record may have different similar results, merge them.
                        merged_results = self._merge_similar_results(results[index - 1].similar_results,
                                                                     results[index + 1].similar_results)
                        # 删除当前记录
                        # delete current no result record
                        results.pop(index)
                        # 当前这个无结果的记录被删除 index 要 -1
                        # 现在的 index 就是之前的 index+1
                        if self._compare_two_results(results, index - 1, index):
                            # choose previous record
                            results[index - 1].similar_results = merged_results
                            results[index - 1].end_time_ms = results[index].end_time_ms
                            results[index - 1].db_end_time_offset_ms = results[index].db_end_time_offset_ms
                            # re-calculate the played_duration
                            results[index - 1].played_duration_ms = results[index - 1].end_time_ms - results[
                                index - 1].start_time_ms

                            results.pop(index)
                            # delete record behind no-result record 删除后面这个记录, 不需要修改index
                            # no need to change the index
                        else:
                            # choose next record
                            results[index].similar_results = merged_results
                            results[index].start_time_ms = results[index - 1].start_time_ms
                            results[index].db_begin_time_offset_ms = results[index - 1].db_begin_time_offset_ms
                            results[index].played_duration_ms = \
                                results[index].end_time_ms - results[index].start_time_ms
                            results.pop(index - 1)
                            index -= 1
                            # delete previous record the index need - 1 删除了之前的记录，需要把index -1

                        # when the current index been deleted, all the follows index should minus 1
                        index -= 1
            index += 1
        """
        1. played duration
        2. db_end_time
        """

        return results

    def _swap_result(self):
        pass

    def _merge_results_with_simple_filter(self, results) -> list:
        """
        Merge the results
        :return:
        """
        merged_results = []

        if results:

            # init
            if results[0].sample_begin_time_offset_ms:
                # 如果第一个 result 有识别到结果，把开始时间改为 sample_begin_time_offset_ms
                results[0].start_time_ms = results[0].sample_begin_time_offset_ms

            # 先把第 0 个元素给 merged_results 初始化 merged_results
            merged_results = [results[0], ]

            results_count = len(results)
            # 从第 1 个元素开始遍历
            for i in range(1, results_count):

                # 上一个结果
                last_result = merged_results[-1]

                # 不同文件,直接跳过后面的处理。
                if results[i].filename != last_result.filename:
                    merged_results.append(results[i])
                    continue

                # 判断 前一个 result 是否在当前的 similar result 里
                # Determine whether the previous result is in the current similar result
                # 在的话就把它换出来，然后把当前的 result 放进 similar 里
                # If so, just swap it out and put the current result into the similar

                if results[i].status_code == ACRCloudStatusCode.ACR_ERR_CODE_OK:
                    if results[i].similar_results:
                        for sr in results[i].similar_results:
                            # compare
                            if last_result.acrid == sr.acrid:
                                results[i].title = sr.title
                                results[i].acrid = sr.acrid
                                if hasattr(results[i], 'audio_id'):
                                    results[i].audio_id = sr.audio_id
                                    results[i].bucket_id = sr.bucket_id
                                results[i].score = 100
                                results[i].sample_begin_time_offset_ms = sr.sample_begin_time_offset_ms
                                results[i].sample_end_time_offset_ms = sr.sample_end_time_offset_ms

                                results[i].played_duration_ms = \
                                    sr.sample_end_time_offset_ms - sr.sample_begin_time_offset_ms

                                # swap
                                results[i].similar_results.append(results[i].primary_result)
                                results[i].primary_result = sr
                                results[i].similar_results.remove(sr)
                                break

                # 如果当前这条记录跟上一条记录 title 一样
                # If the current record is the same as the previous title
                if is_title_similar_or_equal(results[i].title, last_result.title,
                                             self.filter_title_threshold):
                    # if self.results[i].title.lower() == last_result.title.lower():
                    # 这里要加个 db_offset
                    # 如果有识别到结果的，就把结束时间 改为sample_end_time_offset_ms
                    if results[i].sample_end_time_offset_ms:

                        end_time_ms = results[i].start_time_ms + results[i].sample_end_time_offset_ms

                        last_result.end_time_ms = end_time_ms

                        last_result.played_duration_ms = last_result.end_time_ms - last_result.start_time_ms

                        # 合并 similar results 并且 将 score 改为最高的

                        for csr in results[i].similar_results:
                            is_duplicate = False
                            for lsr in last_result.similar_results:
                                if csr.acrid == lsr.acrid:
                                    is_duplicate = True
                                    if csr.score > lsr.score:
                                        lsr.score = csr.score
                            if not is_duplicate:
                                last_result.similar_results.append(csr)
                    else:
                        # no result
                        last_result.played_duration_ms += results[i].played_duration_ms
                        last_result.end_time_ms = results[i].end_time_ms

                    # 两次以上加起来的播放时间如果大于 10 基本确定100%了
                    # if the playerd duration > 10 it can be considered 100% confidence score
                    if last_result.status_code == ACRCloudStatusCode.ACR_ERR_CODE_OK \
                            and last_result.played_duration_ms > 10 * 1000:
                        last_result.score = 100

                else:
                    # 当前这条记录跟上一条记录不一样
                    # 如果有结果更改,开始时间为识别到结果的 sample offset
                    if results[i].sample_begin_time_offset_ms:
                        results[i].start_time_ms += results[i].sample_begin_time_offset_ms

                        results[i].end_time_ms = results[i].start_time_ms + results[i].sample_end_time_offset_ms

                    # 初始化当前的结果的开始时间为上一个结果的结束时间

                    # 对 No Result 的处理
                    if last_result.status_code == ACRCloudStatusCode.NO_RESULT_CODE:
                        last_result.end_time_ms = results[i].start_time_ms
                        last_result.played_duration_ms = last_result.end_time_ms - last_result.start_time_ms

                    if results[i].status_code == ACRCloudStatusCode.NO_RESULT_CODE:
                        last_result.end_time_ms = last_result.start_time_ms + last_result.played_duration_ms
                        results[i].start_time_ms = last_result.end_time_ms
                        results[i].played_duration_ms = results[i].end_time_ms - results[i].start_time_ms

                    # 只有不一样的时候需要加入到结果中，因为一样的话只需要修改前一个结果
                    merged_results.append(results[i])

                # # handle millisecond to second error
                # # Forced change the next result's start_time to last result's end time
                if i < results_count - 1:
                    r = results[i]
                    r_next = results[i + 1]
                    if r.filename == r_next.filename:
                        r_current_end = int(r.end_time_ms / 1000)
                        r_next_start = int(r_next.start_time_ms / 1000)
                        if r_current_end - r_next_start > 0:
                            r_next.start_time_ms = r.end_time_ms

        return merged_results

    @staticmethod
    def _merge_similar_results(results_a: List[Music], results_b: List[Music]) -> List[Music]:
        """
        Merge two List[Music] to a single List[Music] (Union Set) and change the score.
        :param results_a:
        :param results_b:
        :return: merged List[Music]
        """
        import copy

        merged_results = copy.deepcopy(results_a)

        for a_result in results_a:
            for b_result in results_b:
                is_exists = False

                if a_result.acrid == b_result.acrid:
                    is_exists = True
                    if a_result.score < b_result.score:
                        a_result.score = b_result.score

                if not is_exists:
                    merged_results.append(b_result)

        return merged_results

    @staticmethod
    def _parse_similar_results(similar_results) -> list:
        """
        Get similar results
        :param similar_results:
        :return:
        """

        similar_results_list = []

        if similar_results:
            try:
                similar_results_list = [f'{sr.get("title")} [{sr.get("score")}|{sr.get("acrid")}]'
                                        for sr in similar_results]
            except Exception as e:
                print(str(e))

        return similar_results_list

    def export_to_csv(self, results: list, report_filename: str) -> None:
        """
        export the result to csv format
        :param results:
        :param report_filename:
        :return:
        """
        if not any(results):
            return

        suffix = '.csv'

        keys = list(results[0].to_dict().keys())
        # using utf-8-sig: Avoid using excel display wrong characters. F Microsoft.

        keys.insert(3, 'start_time')
        keys.insert(4, 'end_time')
        # move start_time_ms and end_time_ms to the end
        keys.remove('start_time_ms')
        keys.remove('end_time_ms')
        keys += ['start_time_ms', 'end_time_ms']

        report_full_filename = f'{report_filename}{suffix}'

        with open(report_full_filename, 'w', encoding="utf-8-sig") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            for r in results:
                res = r.to_dict()
                res['similar_results'] = '|##|'.join(self._parse_similar_results(res['similar_results']))
                res['start_time'] = get_human_readable_time(res['start_time_ms'] / 1000)
                res['end_time'] = get_human_readable_time(res['end_time_ms'] / 1000)
                dict_writer.writerow(res)

        logger.info(f'The results are exported in {report_full_filename}')

    def export_to_different_csv(self, results: list, report_filename: str) -> None:
        """
        Export the results to a different file

        :param results:
        :param report_filename
        :return:
        """
        suffix = '.csv'
        keys = list(results[0].to_dict().keys())
        keys.insert(3, 'start_time')
        keys.insert(4, 'end_time')
        # move start_time_ms and end_time_ms to the end
        keys.remove('start_time_ms')
        keys.remove('end_time_ms')
        keys += ['start_time_ms', 'end_time_ms']

        report_filenames = []
        tmp = ''
        for r in results:
            if tmp != r.filename:
                tmp = r.filename
                report_full_filename = f'{report_filename}_{r.filename}{suffix}'
                report_filenames.append(report_full_filename)
                with open(report_full_filename, 'w', encoding="utf-8-sig") as f:
                    dict_writer = csv.DictWriter(f, keys)
                    dict_writer.writeheader()

        for r in results:
            report_full_filename = f'{report_filename}_{r.filename}{suffix}'

            with open(report_full_filename, 'a', encoding="utf-8-sig") as f:
                dict_writer = csv.DictWriter(f, keys)
                res = r.to_dict()
                res['similar_results'] = '|##|'.join(self._parse_similar_results(res['similar_results']))
                res['start_time'] = get_human_readable_time(res['start_time_ms'] / 1000)
                res['end_time'] = get_human_readable_time(res['end_time_ms'] / 1000)
                dict_writer.writerow(res)

        for i in report_filenames:
            logger.info(f'The results are exported in {i}')

    @staticmethod
    def export_to_json(results: list, report_filename: str):
        """
        export the result to json format
        :param results:
        :param report_filename:
        :return:
        """
        if not any(results):
            return
        suffix = '.json'
        report_full_filename = f'{report_filename}{suffix}'
        result_dict = []
        for res in results:
            result_dict.append(res.to_dict())

        with open(report_full_filename, 'w', encoding="utf-8") as f:
            f.write(json.dumps(result_dict))

        logger.info(f'The results are exported in {report_full_filename}')

    def export(self, results: list, report_filename: str, output_format):
        if output_format == 'json':
            self.export_to_json(results, report_filename)
        else:
            if self.split_results:
                self.export_to_different_csv(results, report_filename)
            else:
                self.export_to_csv(results, report_filename)

    def scan_target(self, target: str):
        """
        scan a target (a file or a folder)
        :param target: target path
        :return:
        """
        if not os.path.exists(target):
            logger.warning(f'Not Exist {target}')
            sys.exit()

        total_music_results = []
        total_custom_file_results = []

        if os.path.isfile(target):
            # scan a single file
            music_results, custom_file_results = self._scan(target)
            total_music_results = music_results
            total_custom_file_results = custom_file_results
        elif os.path.isdir(target):
            # scan folder
            file_list = []
            for root, dirnames, filenames in os.walk(target):
                for filename in filenames:
                    full_filename = os.path.join(root, filename)
                    file_list.append(full_filename)
            logger.info(f'file list: {file_list}')
            for file in file_list:
                music_results, custom_file_results = self._scan(file)
                total_music_results += music_results
                total_custom_file_results += custom_file_results
        return total_music_results, total_custom_file_results

    def scan_main(self, target: str, output: str, output_format: str) -> None:
        """
        scan a target (a file or a folder)
        :param target: target path
        :param output: output path (must be a folder name)
        :param output_format: the format of the output report json or csv
        """
        logger.info(f'Scan type: {self.scan_type}')
        total_music_results, total_custom_file_results = self.scan_target(target)

        output_music_filenames = {
            'music': f'{target}_music',
            'merged_music': f'{target}_with_duration_music',
            'filtered_music': f'{target}_filtered_music',
        }
        output_custom_filenames = {
            'custom': f'{target}_custom_file',
            'merged_custom_file': f'{target}_with_duration_custom_file',
            'filtered_custom_file': f'{target}_filtered_custom_file',
        }

        music_output_filename = output_music_filenames['music']
        custom_file_output_filename = output_custom_filenames['custom']

        if self.with_duration:
            music_output_filename = output_music_filenames['merged_music']
            custom_file_output_filename = output_custom_filenames['merged_custom_file']

            total_music_results = self._merge_results_with_simple_filter(total_music_results)
            total_custom_file_results = self._merge_results_with_simple_filter(total_custom_file_results)
            if self.filter_results:
                music_output_filename = output_music_filenames['filtered_music']
                custom_file_output_filename = output_custom_filenames['filtered_custom_file']

                total_music_results = self._filter_results(total_music_results)
                total_custom_file_results = self._filter_results(total_custom_file_results)

        if is_file(output):
            dirname = os.path.dirname(output)
            create_folders(dirname)  # create
            filename_without_ext = os.path.splitext(output)[0]
            if self.scan_type == ScanType.SCAN_TYPE_BOTH:
                music_output_filename = f'{filename_without_ext}_music'
                custom_file_output_filename = f'{filename_without_ext}_custom_file'
            else:
                music_output_filename = filename_without_ext
                custom_file_output_filename = filename_without_ext

        if is_folder(output):
            folder_path = create_folders(output)
            target_music_basename = os.path.basename(music_output_filename)
            target_custom_basename = os.path.basename(custom_file_output_filename)
            music_output_filename = folder_path + target_music_basename
            custom_file_output_filename = folder_path + target_custom_basename

        if self.scan_type == ScanType.SCAN_TYPE_MUSIC:
            self.export(total_music_results, music_output_filename, output_format)
            return
        if self.scan_type == ScanType.SCAN_TYPE_CUSTOM:
            self.export(total_custom_file_results, custom_file_output_filename, output_format)
            return
        if self.scan_type == ScanType.SCAN_TYPE_BOTH:
            self.export(total_music_results, music_output_filename, output_format)
            self.export(total_custom_file_results, custom_file_output_filename, output_format)
            return
