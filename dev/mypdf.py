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
show.set(show=False)

LOGGER = logging.getLogger('capture')
exc_msg = 'PDF document parsing failed'


class PDF:
    fmt_check = [[(0, "Office of the Sheriff"),
                  (1, "Department of Correction"),
                  (10, "#"),
                  (12, "Length of Stay #"),
                  (13, "Length of Stay"),
                  (24, "days"),
                  (37, "Age Profile")],
                 [(0, "Office of the Sheriff"),
                  (1, "Department of Correction"),
                  (2, "Daily Jail Population Statistics"),
                  (3, "Laurie Smith, Sheriff"),
                  (10, "Length of Stay"),
                  (11, "Length of Stay"),
                  (26, "Age Profile")]]

    def __init__(self, pdf_file: str, text_file: str) -> object:
        self.pdf_file = pdf_file
        self.text_file = text_file
        self.text = ""
        self.data = dict()
        self.check_target(self.text_file)
        self.fmt = -1

    def __call__(self, nil=None):
        self.to_text()
        self.write()
        fmt = self.determine_format()
        show(fmt)
        if fmt == 0:
            self.parse_fmt0()
        elif fmt == 1:
            self.parse_fmt1()
        else:
            return None
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
                        LOGGER.error("\nError " + repr(tet.get_errnum())
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

    def determine_format(self) -> int:
        doc = self.text.split('\n')
        def test_fmt(check: list) -> bool:
            for c in check:
                print("Checking line: {} is '{}' should be '{}'".format(c[0], doc[c[0]], c[1]))
                if doc[c[0]] != c[1]:
                    return False
            return True

        for fmt, check in enumerate(self.fmt_check):
            if test_fmt(check):
                self.fmt = fmt
                return fmt

        raise ValueError('Unrecognizable PDF format!')

    def parse_fmt0(self):
        LOGGER.debug("Parsing PDF document - format 0")
        self.data = dict()
        exc_msg = 'PDF document parsing failed - line: {}'

        doc = self.text.split('\n')
        d = self.data

        # for i, t in enumerate(doc):
        #     LOGGER.debug("line {:2d}: {}".format(i, t))

        # Lines ending with "%"
        for ln in [14, 15, 20, 21, 27, 28, 33, 34, 45, 46, 47, 48, 49]:
            # print("Line: {}  char: {}".format(ln, doc[ln][-1]))
            if doc[ln][-1] != "%":
                raise ValueError(exc_msg.format(ln))

        # ---------- Parse the Data -----------------
        # Date & time
        def get_date(line):
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
            d['at'] = pytz.timezone('US/Pacific').localize \
                (datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))
            d['Year'] = d['at'].year
            d['Month'] = d['at'].month
            d['Day'] = d['at'].day
            d['Hour'] = d['at'].hour
            d['Minute'] = d['at'].minute
            d['DayOfWeek'] = d['at'].isoweekday()
            d['AsOfDate'] = d['at'].replace(microsecond=0).isoformat()

        get_date(doc[6])

        # Totals
        def l07(line):
            m = re.match("Total Pop: ([\d,]+).*Stay: (\d+)", line)
            d['Total'] = toint(m.group(1))
            d['AvgStay'] = toint(m.group(2))

        l07(doc[7])

        # Men / Women
        def l11(line):
            m = re.match("Men: ([\d,]+).*Women: ([\d,]+)", line)
            d['Men'] = toint(m.group(1))
            d['Wmn'] = toint(m.group(2))

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
            d[c[1]] = one_num(doc[c[0]])

        show(d)

    def parse_fmt1(self):
        LOGGER.debug("Parsing PDF document - format 1")
        self.data = dict()

        lines = self.text.split('\n')
        d = self.data

        # ---------- Parse the Data -----------------
        # Date & time
        d['at'] = get_date(lines[5])
        d['Year'] = d['at'].year
        d['Month'] = d['at'].month
        d['Day'] = d['at'].day
        d['Hour'] = d['at'].hour
        d['Minute'] = d['at'].minute
        d['DayOfWeek'] = d['at'].isoweekday()
        d['AsOfDate'] = d['at'].replace(microsecond=0).isoformat()

        m = re.match("Total Pop: ([\d,]+).*Stay: (\d+)", lines[6])
        d['Total'] = toint(m.group(1))
        d['AvgStay'] = toint(m.group(2))

        m = re.match("Men: ([\d,]+).*Women: ([\d,]+)", lines[9])
        d['Men'] = toint(m.group(1))
        d['Wmn'] = toint(m.group(2))

        d['MenFlnySent'] = toint(re.match("Felony Sentenced: ([\d,]+)", lines[7]).group(1))
        d['MenFlnySentStay'] = one_num(lines[12])
        d['WmnFlnySent'] = one_num(lines[14])
        d['WmnFlnySentStay'] = one_num(lines[16])

        d['MenMisdSent'] = toint(re.match("Misd. Sentenced: ([\d,]+)", lines[8]).group(1))
        d['MenMisdSentStay'] = one_num(lines[13])
        d['WmnMisdSent'] = one_num(lines[15])
        d['WmnMisdSentStay'] =  one_num(lines[17])

        d['MenFlnyUnsent'] = toint(re.match("Felony Unsentenced: ([\d,]+)", lines[18]).group(1))
        d['MenFlnyUnsentStay'] = one_num(lines[20])
        d['WmnFlnyUnsent'] = one_num(lines[22])
        d['WmnFlnyUnsentStay'] = one_num(lines[24])

        d['MenMisdUnsent'] = toint(re.match("Misd. Unsentenced: ([\d,]+)", lines[19]).group(1))
        d['MenMisdUnsentStay'] = one_num(lines[21])
        d['WmnMisdUnsent'] = one_num(lines[23])
        d['WmnMisdUnsentStay'] = one_num(lines[25])


        d['Age18Less'] = toint(re.match("\<18: ([\d,]+)", lines[27]).group(1))
        d['Age18_24'] = toint(re.match("18-24: ([\d,]+)", lines[28]).group(1))
        d['Age25_34'] = toint(re.match("25-34: ([\d,]+)", lines[29]).group(1))
        d['Age35_44'] = toint(re.match("35-44: ([\d,]+)", lines[30]).group(1))
        d['Age45_54'] = toint(re.match("45-54: ([\d,]+)", lines[31]).group(1))
        d['Age55Plus'] = toint(re.match("55\+: ([\d,]+)", lines[32]).group(1))

        show(d)


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


def get_date(line: str) ->  datetime.datetime:
    LOGGER.debug("Converting datetime string: {}".format(line))
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
    LOGGER.debug("Date: {}/{}/{}  time: {}:{:02d}".format(month, day, year, hour, minute))
    return pytz.timezone('US/Pacific').localize \
        (datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))


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

