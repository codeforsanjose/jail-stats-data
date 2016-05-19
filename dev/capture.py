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
import sqlite3 as lite
from PDFlib.TET import *
from apscheduler.schedulers.background import BackgroundScheduler

from config import _SCHEDULER, _DEBUG_G, _DEBUG, _DATA_SOURCE, _DATABASE, _GSPREAD, config_init
from parse_pdf import parse_text_file
from spreadsheet import Spreadsheet

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()


# Init
config_init()

# Log setup
import logsetup as logsetup
logsetup.configure_log('capture')
logsetup.configure_log('apscheduler')
LOGGER = logging.getLogger('capture')


db_name = "/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db"
sched = BackgroundScheduler()
sched.configure(logger=LOGGER, job_defaults=dict(coalesce=True, misfire_grace_time=1, max_instances=1), timezone=_SCHEDULER['timezone'])

SYS_SHUTDOWN = False
EXIT_CODE = 0
_OPTIONS = argparse.Namespace()

exc_msg = lambda ex: "An exception of type {0} occured. Arguments:\n{1!r}".format(type(ex).__name__, ex.args)

def download_pdf():
    LOGGER.debug("Retrieving PDF...")
    retries = _DATA_SOURCE['retries']
    retry_delay = _DATA_SOURCE['retry_delay']
    url = _DATA_SOURCE['url']
    localFile = _DATA_SOURCE['archive_pdf']()

    for n in range(retries):
        try:
            urlretrieve(url, localFile)
            return localFile
        except:
            print_exc()
            LOGGER.warning("Retrieve failed!  Retrying in: {} seconds...".format(retry_delay))
            time.sleep(retry_delay)
            retry_delay *= 2


def pdf_to_text(in_file, outFile):
    separator = "\n"

    try:
        try:

            tet = TET()

            if (sys.version_info[0] < 3):
                raise Exception("Must be run under Python3!")

            with open(outFile, 'w', 2, 'utf-8') as fp:

                docoptlist = ""
                doc = tet.open_document(in_file, docoptlist)

                if (doc == -1):
                    raise Exception("Error " + repr(tet.get_errnum()) + "in "
                                    + tet.get_apiname() + "(): " + tet.get_errmsg())

                # get number of pages in the document */
                n_pages = int(tet.pcos_get_number(doc, "length:pages"))
                LOGGER.debug("Page count: {:d}".format(n_pages))

                # loop over pages in the document */
                for pageno in range(1, n_pages + 1):

                    pageoptlist = "granularity=page"
                    page = tet.open_page(doc, pageno, pageoptlist)

                    if (page == -1):
                        LOGGER.error("Error " + repr(tet.get_errnum()) + "in "
                              + tet.get_apiname() + "(): " + tet.get_errmsg())
                        continue  # try next page */

                    # Retrieve all text fragments; This is actually not required
                    # for granularity=page, but must be used for other granularities.
                    text = tet.get_text(page)
                    while (text != None):
                        data = parse_text_file(text)
                        text += "\n\n"
                        text += pformat(data)
                        fp.write(text)  # print the retrieved text

                        # print a separator between chunks of text
                        fp.write(separator)
                        text = tet.get_text(page)

                    if (tet.get_errnum() != 0):
                        LOGGER.error ("\nError " + repr(tet.get_errnum())
                               + "in " + tet.get_apiname() + "() on page " +
                               repr(pageno) + ": " + tet.get_errmsg() + "\n")

                    tet.close_page(page)

                tet.close_document(doc)

        except TETException:
            LOGGER.error("TET exception occurred:\n[%d] %s: %s" %
                  ((tet.get_errnum()), tet.get_apiname(), tet.get_errmsg()))
            print_tb(sys.exc_info()[2])

        except Exception:
            LOGGER.error("Exception occurred: %s" % (sys.exc_info()[0]))
            print_exc()

    finally:
        tet.delete()
        return data

def save_to_db(stats):
    con = None
    try:
        con = lite.connect(db_name)
        with con:
            con.execute("INSERT INTO daily VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        [stats['Year'],
                        stats['Month'],
                        stats['Day'],
                        stats['Hour'],
                        stats['Minute'],
                        stats['DayOfWeek'],
                        stats['AsOfDate'],
                        stats['Total'],
                        stats['AvgStay'],
                        stats['Men'],
                        stats['MenFlnySent'],
                        stats['MenFlnySentStay'],
                        stats['MenMisdSent'],
                        stats['MenMisdSentStay'],

                        stats['MenFlnyUnsent'],
                        stats['MenFlnyUnsentStay'],
                        stats['MenMisdUnsent'],
                        stats['MenMisdUnsentStay'],

                        stats['Wmn'],

                        stats['WmnFlnySent'],
                        stats['WmnFlnySentStay'],
                        stats['WmnMisdSent'],
                        stats['WmnMisdSentStay'],

                        stats['WmnFlnyUnsent'],
                        stats['WmnFlnyUnsentStay'],
                        stats['WmnMisdUnsent'],
                        stats['WmnMisdUnsentStay'],

                        stats['Age18Less'],
                        stats['Age18_24'],
                        stats['Age25_34'],
                        stats['Age35_44'],
                        stats['Age45_54'],
                        stats['Age55Plus']]
                        )
            LOGGER.info("Saved to database...")

    except lite.IntegrityError:
        LOGGER.warning("The data is already in the database!")

    except Exception as e:
        LOGGER.Exception("save_to_db() failed:")


def save_all_to_gs():
    column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Total', 'AvgStay', 'Men', 'MenFlnySent',
               'MenFlnySentStay', 'MenMisdSent', 'MenMisdSentStay', 'MenFlnyUnsent', 'MenFlnyUnsentStay',
               'MenMisdUnsent', 'MenMisdUnsentStay', 'Wmn', 'WmnFlnySent', 'WmnFlnySentStay', 'WmnMisdSent',
               'WmnMisdSentStay', 'WmnFlnyUnsent', 'WmnFlnyUnsentStay', 'WmnMisdUnsent', 'WmnMisdUnsentStay',
               'Age18Less', 'Age18_24', 'Age25_34', 'Age35_44', 'Age45_54', 'Age55Plus']
    con = None
    all_rows = []
    try:
        con = lite.connect(db_name)
        cur = con.cursor()
        with con:
            cur.execute('SELECT * FROM daily ORDER BY AsOfDate ASC')
            all_rows = cur.fetchall()

    except Exception as e:
        LOGGER.exception("Unable to retrieve data from the database.")

    for row in all_rows:
        data = dict(zip(column_names, row))
        save_row_to_gs(data)


def save_row_to_gs(stats):
    ss = Spreadsheet(data = stats, **_GSPREAD)
    ss.save()


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


def capture():
    localText = _DATA_SOURCE['archive_text']()
    if _OPTIONS.in_file is None:
        localPDF = download_pdf()
        stats = pdf_to_text(localPDF, localText)
    else:
        stats = pdf_to_text(_OPTIONS.in_file, localText)
    LOGGER.debug("localText: {}".format(localText))
    LOGGER.debug(pformat(stats))

    if _DATABASE['active']:
        save_to_db(stats)
    else:
        LOGGER.info("Data not saved - DB is inactive!")

    if _GSPREAD['active']:
        save_row_to_gs(stats)
    else:
        LOGGER.info("Data not saved - DB is inactive!")


def main():
    global _OPTIONS, sched, SYS_SHUTDOWN

    parser = argparse.ArgumentParser(
        description='This program queries the current Santa Clara Country Sheriff Daily Jail Population Statistics, and pushes the data into the "jailstats" SQLite DB.')
    parser.add_argument("-d", "--debug", default=False, dest="debug", action="store_true",
                        help="Display debug messages.")
    parser.add_argument("-i", "--immediate", default=False, dest="immediate", action="store_true",
                        help="Run capture once and exit.")
    parser.add_argument("-a", "--at", dest="hour", type=int, default=7,
                        help="Capture will run once a day at the hour specified (24 hour time!).")
    parser.add_argument("-f", "--file", dest="in_file", type=str,
                        help="Use the specified local PDF file as input.")
    parser.add_argument("-s", "--save", default=False, dest="save_to_db", action="store_true",
                        help="Save ALL current data to the Google spreadsheet.")
    _OPTIONS = parser.parse_args()
    pprint(_OPTIONS)

    # Save to DB
    if _OPTIONS.save_to_db:
        print("Initiating Save To DB...")
        save_all_to_gs()
        sys.exit(EXIT_CODE)

    # Run once!
    if _OPTIONS.immediate:
        capture()
        sys.exit(EXIT_CODE)

    # Didn't specify the hour
    if 0 > _OPTIONS.hour >= 24:
        print("Invalid run time specified - must be an hour between 0 and 23.")
        sys.exit(EXIT_CODE)

    signal.signal(signal.SIGINT, signal_handler)

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

