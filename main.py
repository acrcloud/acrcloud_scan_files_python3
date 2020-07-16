#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from acrscan.lib_downloader import download_lib, current_platform

try:
    from acrscan.acrscan import ACRCloudScan
except ImportError:
    download_lib()
    from acrscan.acrscan import ACRCloudScan
import logging
import yaml
import click
import sys

with open('config.yaml', 'r') as f:
    try:
        config_dict = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        logging.error(exc)

acrcloud_config = config_dict.get('acrcloud')

if acrcloud_config.get('debug'):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


class OptionRequiredIf(click.Option):

    def full_process_value(self, ctx, value):
        value = super(OptionRequiredIf, self).full_process_value(ctx, value)
        if not ctx.params.get('with_duration') and value:
            msg = 'Required --with-duration, if you want filter pls add --with-duration'
            raise click.MissingParameter(ctx=ctx, param=self, message=msg)
        return value


@click.command()
@click.option('--target', '-t',
              help='The target need to scan (a folder or a file).', required=True)
@click.option('--output', '-o', default='',
              help='Output result to this folder. (Must be a folder path)')
@click.option('--format', 'output_format', type=click.Choice(['csv', 'json']),
              help='output format.(csv or json)')
@click.option('--with-duration/--no-duration', '-w', default=False,
              help='Add played duration to the result')
@click.option('--filter-results/--no-filter', default=False,
              help='Enable filter.(It must be used when the with-duration option is on)', cls=OptionRequiredIf)
@click.option('--split-results/--no-split', '-s', default=False,
              help='Each audio/video file generate a report')
@click.option('--scan-type', '-c', type=click.Choice(['music', 'custom', 'both']), default='both',
              help='scan type')
@click.option('--start-time-ms', '-s', default=0,
              help='scan start time')
@click.option('--is-fp/--not-fp', '-f', default=False,
              help='scan fingerprint')
def main(target, output, output_format, with_duration, filter_results, split_results, scan_type, start_time_ms, is_fp):
    ctx = click.get_current_context()
    if not any(v for v in ctx.params.values()):
        click.echo(ctx.get_help())
        ctx.exit()

    platform = current_platform()
    fp_support_platforms = ['linux_64', 'mac']
    if is_fp and platform not in fp_support_platforms:
        print('Your system not support scan fingerprint')
        sys.exit()
    acr = ACRCloudScan(acrcloud_config)
    acr.with_duration = with_duration
    acr.filter_results = filter_results
    acr.split_results = split_results
    acr.scan_type = scan_type
    acr.start_time_ms = start_time_ms * 1000
    acr.is_fingerprint = is_fp
    acr.scan_main(target, output, output_format)


if __name__ == '__main__':
    main()
