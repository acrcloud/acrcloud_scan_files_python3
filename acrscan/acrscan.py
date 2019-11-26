#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from .acrcloud.recognizer import ACRCloudRecognizer
from .acrcloud.recognizer import ACRCloudStatusCode
from .models import *
from typing import List
import json
import logging
import os
import csv
from .utils import is_title_similar_or_equal, get_human_readable_time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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

    def _get_file_duration_ms(self, filename: str) -> int:
        """
        get the file's total play duration
        :param filename: the file position
        :return: the duration of the file (int)
        """
        return self._recognizer.get_duration_ms_by_file(filename)

    def _recognize(self, filename: str, start_time_ms: int) -> dict:
        """
        do recognize and deserialization the json
        :param filename: file position
        :param start_time_ms: start time
        :return: recognize result (dict)
        """
        recognize_length_s = int(self._recognize_length_ms / 1000)

        start_time_s = int(start_time_ms / 1000)

        result = self._recognizer.recognize_by_file(filename, start_time_s, recognize_length_s)

        logger.debug(result)

        return json.loads(result)

    def _scan(self, filename: str) -> (list, list):
        """
        scan a whole file.
        :param filename: filename
        :return: a list response (it will save as an attribute of a object)
        """
        music_results = []
        custom_file_results = []
        duration_ms = self._get_file_duration_ms(filename)
        if not duration_ms:
            duration_ms = 0

        logger.info(f'{filename} File total duration {duration_ms / 1000} seconds')

        for t_ms in range(0, duration_ms, self._recognize_length_ms):
            rec_result = self._recognize(filename, t_ms)
            response = Response.from_dict(rec_result)

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
                if primary_music_result.external_metadata.spotify:
                    music_result.spotify_id = primary_music_result.external_metadata.spotify.track.id
                if primary_music_result.external_metadata.youtube:
                    music_result.youtube_id = primary_music_result.external_metadata.youtube.vid
                if primary_music_result.external_metadata.deezer:
                    music_result.deezer_id = primary_music_result.external_metadata.deezer.track.id
                if primary_music_result.release_date:
                    music_result.release_date = primary_music_result.release_date
                if primary_music_result.label:
                    music_result.label = primary_music_result.label
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
                    custom_file_result.played_duration_ms = \
                        custom_file_result.sample_end_time_offset_ms - custom_file_result.sample_begin_time_offset_ms

        return music_result, custom_file_result

    def _compare_two_result(self, results, results_a_index: int, results_b_index: int) -> bool:
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

        # results_a = self.music_results[results_a_index]
        # results_b = self.music_results[results_b_index]

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

        need_to_delete = []
        # 在音乐的title 相似 db_time 在递增的情况下，删除中间部分的 no result
        for i in range(1, len(results) - 1):
            # traverse the whole results list
            if results[i].status_code == ACRCloudStatusCode.NO_RESULT_CODE:
                # if face a no result record. use fuzzywuzzy to determine the previous and next titles are similar
                # because there are different versions of the same music in the database
                # e.g. Hello, Hello (Remix), Hello (feat. acr)
                if is_title_similar_or_equal(results[i - 1].title, results[i + 1].title,
                                             self.filter_title_threshold):

                    # if the title is the same, should consider the time should be increased
                    # previous_db_end_time + current_played_duration < next_start_time
                    # cause may have some error, so if the difference value < 10 seconds
                    # it should be considered continuous

                    if self._is_continuous(results, i - 1, i + 1):

                        # Because different record may have different similar results, merge them.

                        merged_results = self._merge_similar_results(results[i - 1].similar_results,
                                                                     results[i + 1].similar_results)

                        # if the two titles are similar use 'compare_two_result' to choose which should be selected

                        need_to_delete.append(i)

                        if self._compare_two_result(results, i - 1, i + 1):
                            # choose previous record
                            results[i - 1].similar_results = merged_results
                            results[i - 1].end_time_ms = results[i + 1].end_time_ms
                            results[i - 1].db_end_time_offset_ms = results[i + 1].db_end_time_offset_ms

                            results[i - 1].played_duration_ms = results[i - 1].end_time_ms - results[
                                i - 1].start_time_ms
                            need_to_delete.append(i + 1)
                        else:
                            # choose next record
                            results[i + 1].similar_results = merged_results
                            results[i + 1].start_time_ms = results[i - 1].start_time_ms
                            results[i + 1].db_begin_time_offset_ms = results[i - 1].db_end_time_offset_ms
                            results[i + 1].played_duration_ms = \
                                results[i + 1].end_time_ms - results[i + 1].start_time_ms

                            need_to_delete.append(i - 1)

        """
        1. played duration
        2. db_end_time
        """
        # remove the no result and the repeating element
        filtered_results = [i for j, i in enumerate(results) if j not in need_to_delete]

        # filtered_results = [self.results[0], ]
        #
        # for i in range(1, len(self.results)):
        #
        #
        # self.results = filtered_results
        return filtered_results

    def _swap_result(self):
        pass

    def _merge_results_with_simple_filter(self, results) -> list:
        """
        Merge the results
        :return:
        """
        merged_results = []

        if results:

            # 初始化
            if results[0].sample_begin_time_offset_ms:
                # 如果第一个 result 有识别到结果，把开始时间改为 sample_begin_time_offset_ms
                results[0].start_time_ms = results[0].sample_begin_time_offset_ms

            # 先把第 0 个元素给combined_results 初始化 combined_results
            merged_results = [results[0], ]

            # 从第 1 个元素开始遍历
            for i in range(1, len(results)):

                last_result = merged_results[-1]

                # 不同文件,直接跳过。
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

                    merged_results.append(results[i])

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
        if not results:
            return
        keys = list(results[0].to_dict().keys())
        # keys.append('played_duration_s')

        with open(report_filename, 'w', encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            for r in results:
                res = r.to_dict()
                # res['played_duration_s'] = get_human_readable_time(res['played_duration_ms'] / 1000)
                res['similar_results'] = '|##|'.join(self._parse_similar_results(res['similar_results']))
                res['start_time_ms'] = get_human_readable_time(res['start_time_ms'] / 1000)
                res['end_time_ms'] = get_human_readable_time(res['end_time_ms'] / 1000)
                dict_writer.writerow(res)

        logging.info(f'The results are exported in {report_filename}')

    def scan_file(self, filename: str, output: str, filter_result: bool) -> None:
        """
        scan a file
        :param filename:
        :param output:
        :param filter_result
        :return:
        """
        if not os.path.exists(filename):
            logger.warning(f'Not Exist {filename}')
            return

        if not output:
            prefix = filename
        else:
            prefix = output + os.path.splitext(filename)[1]

        music_output = f'{prefix}_music.csv'
        custom_file_output = f'{prefix}_custom_file.csv'

        merged_music_output = f'{prefix}_merged_music.csv'
        merged_custom_file_output = f'{prefix}_merged_custom_file.csv'

        filtered_music_output = f'{prefix}_filtered_music.csv'
        filtered_custom_file_output = f'{prefix}_filtered_custom_file.csv'

        music_results, custom_file_results = self._scan(filename)

        if self.with_duration:
            merged_music_results = self._merge_results_with_simple_filter(music_results)
            merged_custom_file_results = self._merge_results_with_simple_filter(custom_file_results)

            self.export_to_csv(merged_music_results, merged_music_output)
            self.export_to_csv(merged_custom_file_results, merged_custom_file_output)

            if filter_result:
                filtered_music_results = self._filter_results(merged_music_results)
                filtered_custom_file_results = self._filter_results(merged_custom_file_results)
                self.export_to_csv(filtered_music_results, filtered_music_output)
                self.export_to_csv(filtered_custom_file_results, filtered_custom_file_output)

        self.export_to_csv(music_results, music_output)
        self.export_to_csv(custom_file_results, custom_file_output)

    def scan_folder(self, folder_name: str, output: str, filter_result: bool) -> None:
        """
        Scan a folder
        :param folder_name:
        :param output:
        :param filter_result
        :return:
        """
        if not os.path.exists(folder_name):
            logger.warning(f'Not Exist {folder_name}')
            return

        if not output:
            prefix = folder_name
        else:
            prefix = output

        music_output = f'{prefix}_music.csv'
        custom_file_output = f'{prefix}_custom_file.csv'

        merged_music_output = f'{prefix}_merged_music.csv'
        merged_custom_file_output = f'{prefix}_merged_custom_file.csv'

        filtered_music_output = f'{prefix}_filtered_music.csv'
        filtered_custom_file_output = f'{prefix}_filtered_custom_file.csv'

        filenames = [f'{folder_name}/{i}' for i in os.listdir(folder_name)]

        total_music_results = []
        total_custom_file_results = []

        for file in filenames:
            logger.info(f'scan file {folder_name}/{file}')
            music_results, custom_file_results = self._scan(file)
            total_music_results += music_results
            total_custom_file_results += custom_file_results

        if self.with_duration:
            merged_music_results = self._merge_results_with_simple_filter(total_music_results)
            merged_custom_file_results = self._merge_results_with_simple_filter(total_custom_file_results)

            self.export_to_csv(merged_music_results, merged_music_output)
            self.export_to_csv(merged_custom_file_results, merged_custom_file_output)

            if filter_result:
                filtered_music_results = self._filter_results(merged_music_results)
                filtered_custom_file_results = self._filter_results(merged_custom_file_results)
                self.export_to_csv(filtered_music_results, filtered_music_output)
                self.export_to_csv(filtered_custom_file_results, filtered_custom_file_output)

        self.export_to_csv(total_music_results, music_output)
        self.export_to_csv(total_custom_file_results, custom_file_output)
