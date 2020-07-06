#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ffmpeg
import os
import logging
from fuzzywuzzy import fuzz
import time
import re

logger = logging.getLogger(__name__)


def convert_media_file_to_wav(media_filename: str, ffmpeg_path='ffmpeg') -> str:
    """
    Convert the media file to wav.
    :param ffmpeg_path: ffmpeg bin's path
    :param media_filename:
    :return:
    """
    ffmpeg.run()
    if os.path.splitext(media_filename)[1] == '.wav':
        logger.debug(f'source file is already wav format, there is no need to convert the format. {media_filename}')
        return media_filename

    wav_filename = f'{os.path.splitext(media_filename)[0]}.wav'

    if os.path.exists(wav_filename):
        logger.debug(f'wav file already exsits, delete it.')
        os.remove(wav_filename)

    logger.debug(f'convert the media file to wav')

    ffmpeg.input(media_filename).output(wav_filename, **{'loglevel': 'quiet', 'ac': 1, 'ar': 8000}).run(cmd=ffmpeg_path)

    logger.debug(f'Finished the convert task')

    if os.path.exists(wav_filename):
        return wav_filename

    return ''


def is_title_similar_or_equal(title_a: str, title_b: str, threshold: int) -> bool:
    """
    Determine if two strings are similar
    :param title_a:
    :param title_b:
    :param threshold:
    :return:
    """
    # avoid None == None and Avoid computing
    if title_a == title_b:
        return True

    if fuzz.token_set_ratio(title_a, title_b) >= threshold:
        return True
    return False


def get_human_readable_time(seconds: int) -> str:
    """
    convert seconds to hh:mm:ss format
    :param seconds:
    :return:
    """
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def trim_invalid_file_path_chars(path: str) -> str:
    regex = re.compile(r'[\\/:*?"<>|]')
    return regex.sub(' ', path)


def create_folders(path: str) -> str:
    if not path.endswith(os.sep):
        path = path + os.sep
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def is_file(path: str) -> bool:
    full_path, extension = os.path.splitext(path)
    if full_path and extension:
        return True
    return False


def is_folder(path: str) -> bool:
    full_path, extension = os.path.splitext(path)
    if full_path and not extension:
        return True
    return False

if __name__ == '__main__':
    a = get_human_readable_time(1207)
    print(a)