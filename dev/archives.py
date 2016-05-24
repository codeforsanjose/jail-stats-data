#!/usr/bin/python3
# Maintains the archived PDF and text files.
# Limits the archive directory to files dated within the configured period.

import time
import os
import logging.handlers

from config import get_config

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()

LOGGER = logging.getLogger('capture')

def maintain_archive():
    _, _DATA_SOURCE, _, _, _ = get_config()
    if _DATA_SOURCE['archive_clean_active']:
        clean_dir(_DATA_SOURCE['archive_path'], _DATA_SOURCE['archive_clean_days'])
    else:
        LOGGER.warning("The archive directory: \"{archive_path}\" is not configured for routine maintenance!  This will cause excessive disk space consumption.".format(**_DATA_SOURCE))


def clean_dir(dir, days):
    LOGGER.info("Cleaning the archive directory: {} - deleting files older than {} days:".format(dir, days))
    now = time.time()
    cutoff = now - (days * 86400)

    for f in os.listdir(dir):
        fullpath = os.path.join(dir, f)
        filedate = os.stat(fullpath).st_mtime
        if  filedate < cutoff:
            if os.path.isfile(fullpath):
                LOGGER.info("Deleted: {}".format(fullpath))
                os.remove(fullpath)
