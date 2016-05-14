#!/usr/bin/python3
# Download current Incarceration Stats and load into DB
#


import re
import datetime, time
import os, sys
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
from config import _SCHEDULER, _DEBUG_G, _DEBUG, _DATA_SOURCE, _DATABASE, config_init

config_init()

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()

# Log setup
import logsetup as logsetup

logsetup.configure_log_d(__name__)
logsetup.configure_log_d('apscheduler')
LOGGER = logging.getLogger(__name__)


db_name = "/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db"
sched = BackgroundScheduler()
sched.configure(logger=LOGGER, job_defaults=dict(coalesce=True, misfire_grace_time=1, max_instances=1), timezone=_SCHEDULER['timezone'])

SYS_SHUTDOWN = False
EXIT_CODE = 0
_OPTIONS = argparse.Namespace()

def parse_text_file(text):
    data = dict()

    def toint(x):
        return int(x.replace(',', ''))
    def oneNum(x):
        m = re.match(".*?([\d,]+)$", x)
        return toint(m.group(1))

    def noop(line):
        return
    def l06(line):
        def p(x):
            if x is None:
                return 0
            return int(x)
        m = re.match("At (1[012]|[1-9]):?([0-5][0-9])?(?:\s)?(?i)(am|pm) on: (0?[1-9]|1[012])[- /.](0?[1-9]|[12][0-9]|3[01])[- /.]((?:19|20)\d\d)$", line)
        hour = p(m.group(1))
        if m.group(3).lower() == 'pm':
            hour += 12
        minute = p(m.group(2))
        month = p(m.group(4))
        day = p(m.group(5))
        year = p(m.group(6))
        # print("Date: {}/{}/{}  time: {}:{:02d}".format(month, day, year, hour, minute))
        data['at'] = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    def l07(line):
        m = re.match("Total Pop: ([\d,]+).*Stay: (\d+)", line)
        data['Total'] = toint(m.group(1))
        data['AvgStay'] = toint(m.group(2))

    def l11(line):
        m = re.match("Men: ([\d,]+).*Women: ([\d,]+)", line)
        data['Men'] = toint(m.group(1))
        data['Wmn'] = toint(m.group(2))

    def l08(line):
        data['MenFlnySent'] = oneNum(line)
    def l16(line):
        data['MenFlnySentStay'] = oneNum(line)
    def l18(line):
        data['WmnFlnySent'] = oneNum(line)
    def l22(line):
        data['WmnFlnySentStay'] = oneNum(line)

    def l09(line):
        data['MenMisdSent'] = oneNum(line)
    def l17(line):
        data['MenMisdSentStay'] = oneNum(line)
    def l19(line):
        data['WmnMisdSent'] = oneNum(line)
    def l23(line):
        data['WmnMisdSentStay'] = oneNum(line)
        
    def l25(line):
        data['MenFlnyUnsent'] = oneNum(line)
    def l29(line):
        data['MenFlnyUnsentStay'] = oneNum(line)
    def l31(line):
        data['WmnFlnyUnsent'] = oneNum(line)
    def l35(line):
        data['WmnFlnyUnsentStay'] = oneNum(line)

    def l26(line):
        data['MenMisdUnsent'] = oneNum(line)
    def l30(line):
        data['MenMisdUnsentStay'] = oneNum(line)
    def l32(line):
        data['WmnMisdUnsent'] = oneNum(line)
    def l36(line):
        data['WmnMisdUnsentStay'] = oneNum(line)

    def l38(line):
        data['Age18Less'] = oneNum(line)
    def l39(line):
        data['Age18_24'] = oneNum(line)
    def l40(line):
        data['Age25_34'] = oneNum(line)
    def l41(line):
        data['Age35_44'] = oneNum(line)
    def l42(line):
        data['Age45_54'] = oneNum(line)
    def l43(line):
        data['Age55Plus'] = oneNum(line)

    flist = []
    for i in range(51):
        flist.append(noop)
    flist[6] = l06
    flist[7] = l07
    flist[8] = l08
    flist[9] = l09
    flist[11] = l11
    flist[16] = l16
    flist[17] = l17
    flist[18] = l18
    flist[19] = l19
    flist[22] = l22
    flist[23] = l23
    flist[25] = l25
    flist[26] = l26
    flist[29] = l29
    flist[30] = l30
    flist[31] = l31
    flist[32] = l32
    flist[35] = l35
    flist[36] = l36
    flist[38] = l38
    flist[39] = l39
    flist[40] = l40
    flist[41] = l41
    flist[42] = l42
    flist[43] = l43

    for i, t in enumerate(text.split('\n')):
        LOGGER.debug("line {:2d}: {}".format(i, t))
        flist[i](t)

    return data

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


def pdf_to_text(inFile, outFile):
    separator = "\n"

    try:
        try:

            tet = TET()

            if (sys.version_info[0] < 3):
                raise Exception("Must be run under Python3!")

            with open(outFile, 'w', 2, 'utf-8') as fp:

                docoptlist = ""
                doc = tet.open_document(inFile, docoptlist)

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
            con.execute("INSERT INTO daily VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        [stats['at'].year,
                        stats['at'].month,
                        stats['at'].day,
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

    except lite.IntegrityError as e:
        LOGGER.warning("The data is already in the database!")

    except lite.Error as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        LOGGER.error("An error occurred: {}\n   type: {}  file: {}:{}".format(e.args[0], exc_type, fname, exc_tb.tb_lineno))

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

def capture():
    localText = _DATA_SOURCE['archive_text']()
    if _OPTIONS.inFile is None:
        localPDF = download_pdf()
        stats = pdf_to_text(localPDF, localText)
    else:
        stats = pdf_to_text(_OPTIONS.inFile, localText)
    LOGGER.debug("localText: {}".format(localText))
    LOGGER.debug(pformat(stats))
    if _DATABASE['active']:
        save_to_db(stats)
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
    parser.add_argument("-f", "--file", dest="inFile", type=str,
                        help="Use the specified local PDF file as input.")
    _OPTIONS = parser.parse_args()
    pprint(_OPTIONS)

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


'''
CREATE TABLE IF NOT EXISTS main.daily(
  Year INT,
  Month INT,
  Day INT,
  Total INT,
  AvgStay INT,

  Men INT,

  MenFlnySent INT,
  MenFlnySentStay INT,
  MenMisdSent INT,
  MenMisdSentStay INT,

  MenFlnyUnsent INT,
  MenFlnyUnsentStay INT,
  MenMisdUnsent INT,
  MenMisdUnsentStay INT,

  Wmn INT,

  WmnFlnySent INT,
  WmnFlnySentStay INT,
  WmnMisdSent INT,
  WmnMisdSentStay INT,

  WmnFlnyUnsent INT,
  WmnFlnyUnsentStay INT,
  WmnMisdUnsent INT,
  WmnMisdUnsentStay INT,

  Age18Less INT,
  Age18_24 INT,
  Age25_34 INT,
  Age35_44 INT,
  Age45_54 INT,
  Age55Plus INT
  );
CREATE UNIQUE INDEX main.daily_pk ON daily(Year, Month, Day);
'''
