#!/usr/bin/python3
# Download current Incarceration Stats and load into DB

import re
import datetime
import time
import pytz
import os
import sys
import signal
import select
from traceback import print_tb, print_exc
import argparse
import logging
import logging.handlers
from urllib.request import urlretrieve
import requests
import sqlite3 as lite
from PDFlib.TET import *
from apscheduler.schedulers.background import BackgroundScheduler

from myconfig import config_init
from mypdf import PDF
from myspreadsheet import Spreadsheet
import mylogsetup
from myarchives import maintain_archive
import mydb

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()


sched = BackgroundScheduler()

SYS_SHUTDOWN = False
EXIT_CODE = 0
_OPTIONS = argparse.Namespace()
LOGGER = logging.Logger('capture')

exc_msg = lambda ex: "An exception of type {0} occured. Arguments:\n{1!r}".format(type(ex).__name__, ex.args)

class MyError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class Download(object):
    def __init__(self, url: str, target: str, retries: int, retry_delay: int, timeout: int = 3) -> object:
        self.url = url
        self.target = target
        self.retries = retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.check_target(self.target)
        show(self.__dict__)

    def __call__(self):
        return self.fetch()

    def check_target(self, target):
        if not os.access(os.path.dirname(target), os.W_OK):
            msg = "Invalid download target (invalid path or write privileges missing): {}".format(self.target)
            LOGGER.error(msg)
            raise MyError(msg)

    def fetch(self):
        global _DATA_SOURCE

        LOGGER.debug("Dowloading: {} --> {}".format(self.url, self.target))
        for n in range(self.retries):
            try:
                show(self.url, self.target, n, self.retries)
                request = requests.get(self.url, timeout=self.timeout, stream=True)
                with open(self.target, 'wb') as fh:
                    for chunk in request.iter_content(1024 * 1024):
                        fh.write(chunk)
                LOGGER.debug("File saved as: {}".format(self.target))
                return self.target
            except FileNotFoundError:
                LOGGER.exception("Invalid download target: {}".format(self.target))
                raise
            except:
                if n <= (self.retries - 1):
                    LOGGER.warning("Download connection failed!  Retrying in: {} seconds...".format(self.retry_delay))
                else:
                    LOGGER.exception("Download failed!")
                    raise
                time.sleep(self.retry_delay)
                self.retry_delay *= 2


def save_all_to_gs():
    global _database

    for row in _database.fetchall():
        stats = dict(zip(_database.column_names, row))
        Spreadsheet(data=stats, **_GSPREAD)()


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def capture():
    global _DATA_SOURCE, _database, _GSPREAD

    localText = _DATA_SOURCE['archive_text']()
    if _OPTIONS.in_file is None:
        LOGGER.debug("Downloading file at: {}".format(_DATA_SOURCE['url']))
        localPDF = Download(url = _DATA_SOURCE['url'],
                            target = _DATA_SOURCE['archive_pdf'](),
                            retries = _DATA_SOURCE['retries'],
                            retry_delay = _DATA_SOURCE['retry_delay'])()
        LOGGER.info("Archived PDF to: {}".format(localPDF))
        stats = PDF(pdf_file = localPDF,
                    text_file = localText)()
    else:
        LOGGER.debug("Processing file at: ")
        stats = PDF(pdf_file = _OPTIONS.in_file,
                    text_file = localText)()
    LOGGER.debug("Saving text file to: {}".format(localText))
    LOGGER.debug("Stats data: {}".format(pformat(stats)))

    # Save to database
    save_ok = _database.save(stats)
    _database.maintain()

    # Write to spreadsheet
    if save_ok or _OPTIONS.save_to_gs:
        Spreadsheet(data=stats, **_GSPREAD)()

    # Cleanup the archive
    maintain_archive()


def main():
    global _OPTIONS, sched, SYS_SHUTDOWN, LOGGER
    global _SCHEDULER, _DATA_SOURCE, _LOGS, _GSPREAD
    global _database

    parser = argparse.ArgumentParser(
        description='This program queries the current Santa Clara Country Sheriff Daily Jail Population Statistics, pushes the data into the "jailstats" SQLite DB, and uploads the data to the Google Spreadsheet.')
    parser.add_argument("-a", "--gs_all", default=False, dest="save_all_to_gs", action="store_true",
                        help="Upload ALL data in the database to the Google spreadsheet.  NOTE: the spreadsheet is NOT cleared, so this may cause duplicates!")
    parser.add_argument("-d", "--debug", default=False, dest="debug", action="store_true",
                        help="Run in test mode, with debug logging.")
    parser.add_argument("-f", "--file", dest="in_file", type=str,
                        help="Specifies a local PDF file as input.")
    parser.add_argument("-s", "--spreadsheet", default=False, dest="save_to_gs", action="store_true",
                        help="Write the data to the Google spreadsheet, even if the data is already present in the SQLite DB.")
    parser.add_argument("env", action="store", type=str, choices=['test', 'prod', 'ptest'],
                        help="The run environment - must be one of the following: test, prod or ptest.")
    parser.add_argument("-m", "--mode", default="immediate", dest="mode", type=str, choices=['immediate', 'scheduled'],
                        help="Must be either \"scheduled\" or \"immediate\".  The default is \"immediate\".")
    _OPTIONS = parser.parse_args()
    show.set(show=_OPTIONS.debug)
    show(_OPTIONS)
    if _OPTIONS.mode == False and _OPTIONS.in_file is not None:
        LOGGER.fatal("You cannot run the app in scheduled mode and specify an input file.  If an input file is specified, the app must be run in IMMEDIATE mode.")
        sys.exit(-1)

    # Load config
    _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD = config_init(_OPTIONS.env)
    # show(_SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD)
    show(_DATABASE['name'], _GSPREAD['name'])

    # Setup logging
    mylogsetup.configure_log('capture')
    mylogsetup.configure_log('apscheduler')
    LOGGER = logging.getLogger('capture')

    LOGGER.debug("Options: %s", pformat(_OPTIONS))

    _database = mydb.DB(**_DATABASE)

    # Save to DB
    if _OPTIONS.save_all_to_gs:
        print("Initiating Save To DB...")
        save_all_to_gs()

    # Run once!
    elif _OPTIONS.mode == 'immediate':
        capture()

    # Run the scheduler.
    elif _OPTIONS.mode == 'scheduled':
        signal.signal(signal.SIGINT, signal_handler)

        sched.configure(logger=LOGGER, job_defaults=dict(coalesce=True, misfire_grace_time=1, max_instances=1),
                        timezone=_SCHEDULER['timezone'])
        sched.start()
        sched.add_job(capture, 'cron', **_SCHEDULER['schedule'])
        sched.print_jobs()

        print('Type "shutdown" to kill the program: ')
        command = ''
        while command.lower() != 'shutdown' and SYS_SHUTDOWN == False:
            i, o, e = select.select([sys.stdin], [], [], 10)
            if (i):
                command = sys.stdin.readline().strip()
                # else:
                #     print ".",

        LOGGER.info('Scheduler shutting down now.')
        sched.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possible

    sys.exit(EXIT_CODE)


if __name__ == "__main__":
    main()
