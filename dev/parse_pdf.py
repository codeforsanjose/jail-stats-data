#!/usr/bin/python3
# Download current Incarceration Stats and load into DB

import re
import datetime
import pytz
import logging

LOGGER = logging.getLogger('capture')
exc_msg = 'PDF document parsing failed'


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


def parse_text_file(text):
    data = dict()
    exc_msg = 'PDF document parsing failed - line: {}'

    doc = text.split('\n')

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
        data['at'] = pytz.timezone('US/Pacific').localize \
            (datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute))
        data['Year'] = data['at'].year
        data['Month'] = data['at'].month
        data['Day'] = data['at'].day
        data['Hour'] = data['at'].hour
        data['Minute'] = data['at'].minute
        data['DayOfWeek'] = data['at'].isoweekday()
        data['AsOfDate'] = data['at'].replace(microsecond=0).isoformat()

    l06(doc[6])

    # Totals
    def l07(line):
        m = re.match("Total Pop: ([\d,]+).*Stay: (\d+)", line)
        data['Total'] = toint(m.group(1))
        data['AvgStay'] = toint(m.group(2))

    l07(doc[7])

    # Men / Women
    def l11(line):
        m = re.match("Men: ([\d,]+).*Women: ([\d,]+)", line)
        data['Men'] = toint(m.group(1))
        data['Wmn'] = toint(m.group(2))

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
        data[c[1]] = one_num(doc[c[0]])

    return data
