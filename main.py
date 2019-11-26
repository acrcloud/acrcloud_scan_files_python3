#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from acrscan.lib_downloader import download_lib

try:
    from acrscan.acrscan import ACRCloudScan
except ImportError:
    download_lib()
    from acrscan.acrscan import ACRCloudScan
import logging
import yaml
import os
import click

with open('config.yaml', 'r') as f:
    try:
        config_dict = yaml.safe_load(f)
        logging.info(config_dict)
    except yaml.YAMLError as exc:
        logging.error(exc)

acrcloud_config = config_dict.get('acrcloud')

logging.basicConfig(level=logging.INFO)

if acrcloud_config.get('debug'):
    logging.basicConfig(level=logging.DEBUG)


class OptionRequiredIf(click.Option):

    def full_process_value(self, ctx, value):
        value = super(OptionRequiredIf, self).full_process_value(ctx, value)
        print(ctx.params.keys())
        if not ctx.params.get('with_duration') and value:
            msg = 'Required --with-duration, if you want filter pls add --with-duration'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


@click.command()
@click.option('--target', '-t', type=click.Path(exists=True), required=True,
              help='The target need to scan (a folder or a file).')
@click.option('--output', '-o', default='', type=click.Path(),
              help='Output result to this folder. (Must be a folder path)')
@click.option('--with-duration/--no-duration', '-w', default=False,
              help='Add played duration to the result')
@click.option('--filter-results/--no-filter', default=False,
              help='Enable filter.(It must be used when the with-duration option is on)', cls=OptionRequiredIf)
def main(target, output, with_duration, filter_results):
    acr = ACRCloudScan(acrcloud_config)
    acr.with_duration = with_duration
    if output:
        if not os.path.exists(output):
            open(output, 'w+')
    if os.path.isdir(target):
        acr.scan_folder(target, output, filter_results)
    elif os.path.isfile(target):
        acr.scan_file(target, output, filter_results)
    else:
        logging.warning("Unsupported target type")


if __name__ == '__main__':
    main()
