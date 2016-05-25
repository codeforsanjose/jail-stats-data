#!/usr/bin/python3

import os, sys
import logging
import logging.handlers
from myconfig import get_config

from pprint import pprint, pformat
from show import show

show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()


def configure_log(name: object) -> None:
    _, _, _, _LOGS, _ = get_config()
    ccon, cfile, cemail = _LOGS['stdout'], _LOGS['file'], _LOGS['email']

    root = logging.getLogger(name)
    root.setLevel(ccon['level'])

    if ccon['active']:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(ccon['level'])
        ch.setFormatter(logging.Formatter(ccon['format'], datefmt=ccon['datefmt']))
        root.addHandler(ch)

    if cfile['active']:
        fh = logging.handlers.RotatingFileHandler(os.path.join(cfile['path'], cfile['filename']), maxBytes=200000,
                                                  backupCount=6)
        fh.setLevel(cfile['level'])
        fh.setFormatter(logging.Formatter(cfile['format'], datefmt=cfile['datefmt']))
        root.addHandler(fh)

    if cemail['active']:
        eh = logging.handlers.SMTPHandler(**cemail['handler'])
        eh.setLevel(cemail['level'])
        eh.setFormatter(logging.Formatter(cemail['format'], datefmt=cfile['datefmt']))
        root.addHandler(eh)



