#!/usr/bin/python3
# Maintains the archived PDF and text files.
# Limits the archive directory to files dated within the configured period.

import time
import os
import logging.handlers

from myconfig import get_config

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()

LOGGER = logging.getLogger('capture')

def maintain_archive():
    _, _DATA_SOURCE, _, _, _ = get_config()
    if _DATA_SOURCE['archive_clean_active']:
        show(_DATA_SOURCE)
        clean_dir(dir_path=_DATA_SOURCE['archive_path'],
                  days=_DATA_SOURCE['archive_retain_days'],
                  prefixes=_DATA_SOURCE['archive_file_prefixes'],
                  suffixes=_DATA_SOURCE['archive_file_suffixes'])
    else:
        LOGGER.warning("The archive directory: \"{archive_path}\" is not configured for routine maintenance!  This will cause excessive disk space consumption.".format(**_DATA_SOURCE))


def clean_dir(dir_path: str, days: int, prefixes: list, suffixes: list):
    def check_prefix(name):
        for prefix in prefixes:
            if name[:len(prefix)] == prefix:
                return True
        return False

    def check_suffix(name):
        for suffix in suffixes:
            if name[-len(suffix):] in suffix:
                return True
        return False

    now = time.time()
    cutoff = now - (days * 86400)
    LOGGER.info("Cleaning the directory: {}\n   - deleting files older than {} days (prior to: {}):".format(dir_path, days, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(cutoff))))
    fl = os.listdir(dir_path)
    show(fl, prefixes, suffixes)
    file_gen = (f for f in fl if check_prefix(f) and check_suffix(f))
    for f in file_gen:
        fullpath = os.path.join(dir_path, f)
        filedate = os.stat(fullpath).st_mtime
        if  filedate < cutoff:
            if os.path.isfile(fullpath):
                LOGGER.info("Deleted: {}".format(fullpath))
                os.remove(fullpath)