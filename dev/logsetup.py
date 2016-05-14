#!/usr/bin/python3

import os, sys
import logging
import logging.handlers
from config import _CONFIG, _DEBUG_G, _LOGS

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()


def configure_log(consoleLevel=logging.DEBUG, name=None, logtofile=False, fileLevel=logging.WARNING, filepath="logs", filename=None):
    root = logging.getLogger(name)
    root.setLevel(consoleLevel)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(consoleLevel)
    ch_formatter = logging.Formatter('[%(asctime)s  %(levelname)-8s %(funcName)s:%(lineno)d] %(message)s', datefmt='%m-%d %H:%M')
    # ch_formatter = logging.Formatter('[%(asctime)s] %(funcName)-20s: %(lineno) -5d: %(levelname)-8s: %(message)s', datefmt='%m-%d %H:%M')
    # ch_formatter = logging.Formatter('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s', datefmt='%m-%d %H:%M')
    ch.setFormatter(ch_formatter)
    root.addHandler(ch)

    if logtofile:
        logfilefullname = os.path.join(filepath, '%s.log' % filename)
        fh = logging.handlers.RotatingFileHandler(logfilefullname, maxBytes=200000, backupCount=6)
        fh.setLevel(fileLevel)
        fh_formatter = logging.Formatter('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
        fh.setFormatter(fh_formatter)
        root.addHandler(fh)
    return


def configure_log_d(name):
    ccon, cfile = _LOGS['stdout'], _LOGS['file']
    
    root = logging.getLogger(name)
    root.setLevel(ccon['level'])

    if ccon['active']:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(ccon['level'])
        ch.setFormatter(logging.Formatter(ccon['format'], datefmt=ccon['datefmt']))
        root.addHandler(ch)

    if cfile['active']:
        fh = logging.handlers.RotatingFileHandler(os.path.join(cfile['path'], cfile['filename']), maxBytes=200000, backupCount=6)
        fh.setLevel(cfile['level'])
        fh.setFormatter(logging.Formatter(cfile['format'], datefmt=cfile['datefmt']))
        root.addHandler(fh)
    return
