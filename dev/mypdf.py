#!/usr/bin/python3
# Download current Incarceration Stats and load into DB

import sys
import os
import re
import datetime
import pytz
import logging
from pprint import pformat
from PDFlib.TET import *

from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()
show.set(show=True)

LOGGER = logging.getLogger('capture')
exc_msg = 'PDF document parsing failed'


class PDF:
    def __init__(self, pdf_file: str, text_file: str) -> object:
        self.pdf_file = pdf_file
        self.text_file = text_file
        self.text = ""
        self.data = dict()
        self.check_target(self.text_file)

    def __call__(self):
        self.to_text()
        self.parse_text()
        self.write()
        return self.data

    def check_target(self, target):
        if not os.access(os.path.dirname(target), os.W_OK):
            msg = "Invalid download target (invalid path or write privileges missing): {}".format(self.target)
            LOGGER.error(msg)
            raise MyError(msg)

    def to_text(self) -> dict:
        try:
            try:
    
                tet = TET()
    
                if (sys.version_info[0] < 3):
                    raise Exception("Must be run under Python3!")
    
                docoptlist = ""
                doc = tet.open_document(self.pdf_file, docoptlist)

                if (doc == -1):
                    raise Exception("Error " + repr(tet.get_errnum()) + "in "
                                    + tet.get_apiname() + "(): " + tet.get_errmsg())

                n_pages = int(tet.pcos_get_number(doc, "length:pages"))
                for pageno in range(1, n_pages + 1):

                    pageoptlist = "granularity=page"
                    page = tet.open_page(doc, pageno, pageoptlist)

                    if (page == -1):
                        LOGGER.error("Error " + repr(tet.get_errnum()) + "in "
                              + tet.get_apiname() + "(): " + tet.get_errmsg())
                        continue  # try next page */

                    text = tet.get_text(page)
                    self.text = ""
                    while (text != None):
                        self.text += text
                        self.text += "\n"
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
            return self.data

    def parse_text(self):
        self.data = dict()
        exc_msg = 'PDF document parsing failed - line: {}'

        doc = self.text.split('\n')

        # for i, t in enumerate(doc):
        #     LOGGER.debug("line {:2d}: {}".format(i, t))

        # ---------- General syntax checks -----------------
        # Check static full doc
        checks = [(0, "Office of the Sheriff"),
                  (1, "Department of Correction"),
                  (10, "#"),
                  (12, "Length of Stay #"),
                  (13, "Length of Stay"),
                  (24, "days"),
                  (37, "Age Profile")]
        for c in checks:
            # print("Checking line: {} is '{}' should be '{}'".format(c[0], doc[c[0]], c[1]))
            if doc[c[0]] != c[1]:
                raise ValueError(exc_msg.format(c[0]))

        # Lines ending with "%"
        for ln in [14, 15, 20, 21, 27, 28, 33, 34, 45, 46, 47, 48, 49]:
            # print("Line: {}  char: {}".format(ln, doc[ln][-1]))
            if doc[ln][-1] != "%":
                raise ValueError(exc_msg.format(ln))

        # ---------- Parse the Data -----------------
        # Date & time
        def l06(line):
            def p(x):
                if x is None:
                    return 0
                return int(x)

            m = re.match \
                    (
                    "At (1[012]|[1-9]):?([0-5][0-9])?(?:\s)?(?i)(am|pm) on: (0?[1-9]|1[012])[- /.](0?[1-9]|[12][0-9]|3[01])[- /.]((?:19|20)\d\d)$",
                    line)
            hour = p(m.group(1))
            if m.group(3).lower() == 'pm':
                hour += 12
            minute = p(m.group(2))
            month = p(m.group(4))
            day = p(m.group(5))
            year = p(m.group(6))
            LOGGER.info("Document date: {}/{}/{}  time: {}:{:02d}".format(month, day, year, hour, minute))
            self.data['at'] = pytz.timezone('US/Pacific').localize \
                (datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))
            self.data['Year'] = self.data['at'].year
            self.data['Month'] = self.data['at'].month
            self.data['Day'] = self.data['at'].day
            self.data['Hour'] = self.data['at'].hour
            self.data['Minute'] = self.data['at'].minute
            self.data['DayOfWeek'] = self.data['at'].isoweekday()
            self.data['AsOfDate'] = self.data['at'].replace(microsecond=0).isoformat()

        l06(doc[6])

        # Totals
        def l07(line):
            m = re.match("Total Pop: ([\d,]+).*Stay: (\d+)", line)
            self.data['Total'] = toint(m.group(1))
            self.data['AvgStay'] = toint(m.group(2))

        l07(doc[7])

        # Men / Women
        def l11(line):
            m = re.match("Men: ([\d,]+).*Women: ([\d,]+)", line)
            self.data['Men'] = toint(m.group(1))
            self.data['Wmn'] = toint(m.group(2))

        l11(doc[11])

        # Single Numbers
        sn = [(8, 'MenFlnySent'),
              (16, 'MenFlnySentStay'),
              (18, 'WmnFlnySent'),
              (22, 'WmnFlnySentStay'),

              (9, 'MenMisdSent'),
              (17, 'MenMisdSentStay'),
              (19, 'WmnMisdSent'),
              (23, 'WmnMisdSentStay'),

              (25, 'MenFlnyUnsent'),
              (29, 'MenFlnyUnsentStay'),
              (31, 'WmnFlnyUnsent'),
              (35, 'WmnFlnyUnsentStay'),

              (26, 'MenMisdUnsent'),
              (30, 'MenMisdUnsentStay'),
              (32, 'WmnMisdUnsent'),
              (36, 'WmnMisdUnsentStay'),

              (38, 'Age18Less'),
              (39, 'Age18_24'),
              (40, 'Age25_34'),
              (41, 'Age35_44'),
              (42, 'Age45_54'),
              (43, 'Age55Plus')]

        for c in sn:
            self.data[c[1]] = one_num(doc[c[0]])

    def write(self):
        with open(self.text_file, 'w', 2, 'utf-8') as fp:
            fp.write(self.text)
            fp.write("\n")
            fp.write(pformat(self.data))


class MyError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

def toint(x):
    return int(x.replace(',', ''))


def one_num(x):
    m = re.match(".*?([\d,]+)$", x)
    return toint(m.group(1))


def line_is(line, value):
    if line != value:
        raise ValueError(exc_msg)


def last_char_is(line, value):
    if line[-1] != value:
        raise ValueError(exc_msg)


