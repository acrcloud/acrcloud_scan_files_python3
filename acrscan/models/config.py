#!/usr/bin/env python 
# -*- coding: utf-8 -*-


class ScanType:
    SCAN_TYPE_MUSIC = 0,
    SCAN_TYPE_CUSTOM = 1,
    SCAN_TYPE_BOTH = 3,


class Config:
    scan_type = ScanType.SCAN_TYPE_MUSIC
