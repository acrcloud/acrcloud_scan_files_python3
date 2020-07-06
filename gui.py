#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from gooey import Gooey, GooeyParser
from acrscan.lib_downloader import download_lib

try:
    from acrscan.acrscan import ACRCloudScan
except ImportError:
    download_lib()
    from acrscan.acrscan import ACRCloudScan
import logging
import yaml


def show_error_modal(error_msg):
    """ Spawns a modal with error_msg"""
    # wx imported locally so as not to interfere with Gooey
    import wx
    app = wx.App()
    dlg = wx.MessageDialog(None, error_msg, 'Error', wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


try:
    with open('config.yaml', 'r') as f:
        config_dict = yaml.safe_load(f)
except yaml.YAMLError as exc:
    logging.error(exc)
except FileNotFoundError as e:
    show_error_modal('Please make sure you fill the config.yaml')

acrcloud_config = config_dict.get('acrcloud')

if acrcloud_config.get('debug'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


@Gooey(progress_regex=r"^INFO:acrscan.acrscan:progress: (?P<current>\d+)/(?P<total>\d+)$",
       progress_expr="current / total * 100", )
def gui():
    parser = GooeyParser(description="ACRCloud File Scanner", )
    parser.add_argument("target", widget="FileChooser")
    parser.add_argument("output", widget="FileSaver")
    parser.add_argument("scan_type", widget='Dropdown', choices=['music', 'custom', 'both'], default='both')
    parser.add_argument("output_format", widget='Dropdown', choices=['csv', 'json'], default='csv')
    parser.add_argument("with_duration", widget='Dropdown', choices=['yes', 'no'], default='no')
    parser.add_argument("filter_results", widget='Dropdown', choices=['yes', 'no'], default='no')

    args = parser.parse_args()

    bool_dict = {"yes": True,
                 "no": False}
    acr = ACRCloudScan(acrcloud_config)
    acr.with_duration = bool_dict.get(args.with_duration)
    acr.filter_results = bool_dict.get(args.filter_results)
    acr.scan_type = args.scan_type

    acr.split_results = False
    acr.start_time_ms = 0
    acr.scan_main(args.target, args.output, args.output_format)


if __name__ == '__main__':
    gui()
