#!/usr/bin/env python 
# -*- coding: utf-8 -*-
from tqdm import tqdm
import os
import platform
import logging
import urllib3
from io import BytesIO

logger = logging.getLogger(__name__)

here = os.path.abspath(os.path.dirname(__file__))

BASE_URL = 'https://raw.githubusercontent.com/acrcloud/acrcloud_sdk_python/master'

download_urls = {
    'mac': f'{BASE_URL}/mac/x86-64/python3/acrcloud/acrcloud_extr_tool.so',
    'linux_64': f'{BASE_URL}/linux/x86-64/python3/acrcloud/acrcloud_extr_tool.so',
    'linux_32': f'{BASE_URL}/linux/x86/python3/acrcloud/acrcloud_extr_tool.so',
    'win64': f'{BASE_URL}/windows/win64/python3/acrcloud/acrcloud_extr_tool.pyd',
    'win32': f'{BASE_URL}/windows/win32/python3/acrcloud/acrcloud_extr_tool.pyd'
}

library_filenames = {
    'mac': f'{here}/acrcloud/acrcloud_extr_tool.so',
    'linux_64': f'{here}/acrcloud/acrcloud_extr_tool.so',
    'linux_32': f'{here}/acrcloud/acrcloud_extr_tool.so',
    'win64': f'{here}/acrcloud/acrcloud_extr_tool.pyd',
    'win32': f'{here}/acrcloud/acrcloud_extr_tool.pyd'
}


def current_platform() -> str:
    """
    Get current platform name.
    :return:
    """
    system = platform.system()
    arch = platform.machine().replace('_', '-')

    if system.startswith('Linux'):
        if arch.endswith('64'):
            return 'linux_64'
        return 'linux_32'
    elif system.startswith('Darwin'):
        return 'mac'
    elif system.startswith('Win'):
        if arch.endswith('64'):
            return 'win64'
        return 'win32'
    raise OSError(f'Unsupported platform: {system} {arch}')


def get_url() -> str:
    """
    get download url
    :return:
    """
    return download_urls[current_platform()]


def download(url: str) -> BytesIO:
    """
    Download a file
    :param url: the url of the file
    :return:
    """
    logger.warning('Start ACRCloud Dependencies download.\n'
                   'Download may take a few minutes.')

    urllib3.disable_warnings()

    with urllib3.PoolManager() as http:
        # Get data from url.
        # set preload_content=False means using stream later.
        data = http.request('GET', url, preload_content=False)

        try:
            total_length = int(data.headers['content-length'])
        except (KeyError, ValueError, AttributeError):
            total_length = 0

        process_bar = tqdm(
            total=total_length,
        )

        # 10 * 1024
        _data = BytesIO()
        for chunk in data.stream(10240):
            _data.write(chunk)
            process_bar.update(len(chunk))
        process_bar.close()

        with open(library_filenames[current_platform()], 'wb') as f:
            f.write(_data.getvalue())

    logger.warning('\nACRCloud library download done.')
    return _data


def download_lib():
    """
    Download the lib
    :return:
    """
    if not check_lib_exists():
        download(get_url())


def check_lib_exists() -> bool:
    """
    Check if the library exists
    :return:
    """
    if os.path.exists(library_filenames[current_platform()]):
        return True
    return False


if __name__ == '__main__':
    download_lib()
