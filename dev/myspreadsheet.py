#!/usr/bin/python3
# Download current Incarceration Stats and load into DB

import gspread
import sys
from oauth2client.service_account import ServiceAccountCredentials
import logging

LOGGER = logging.getLogger('capture')

from pprint import pprint, pformat
from show import show

show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()
show.set(show=True)

def str_to_class(str):
    return getattr(sys.modules[__name__], str)


class Spreadsheet(object):
    def __init__(self, data: dict, active: bool, name: str, credentials_file: str, worksheets: list, mode: str,
                 insert_at: int = 0, debug: bool = False) -> object:
        self.active = active
        self.name = name
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        gcred = gspread.authorize(credentials)
        LOGGER.debug("Opening spreadsheet: {}".format(name))
        self.sheet = gcred.open(name)
        self.ws = dict()
        for wname in worksheets:
            LOGGER.debug("Opening worksheet '{}'".format(wname))
            try:
                ws = self.sheet.worksheet(wname)
                self.ws[wname] = Worksheet(wname, ws, data, mode, insert_at)
            except gspread.SpreadsheetNotFound:
                LOGGER.error("Worksheet: {} not found!", wname)

    def __call__(self):
        return self.save()

    def save(self) -> None:
        if not self.active:
            LOGGER.warning("Data not written to the Spreadsheet - marked inactive!")
            return
        for name, ws in self.ws.items():
            LOGGER.debug("Writing '{}' to Spreadsheet".format(name))
            ws.save()


class Worksheet(object):
    def __init__(self, name: str, ws: gspread.Worksheet, data: dict, mode: str, insert_at: int = 0, debug: bool = False):
        self.name = name
        self.ws = ws
        self.data = str_to_class(name)(data)
        self.mode = mode
        self.insert_at = insert_at
        self.debug = debug
        if self.name != self.data.name:
            raise

    def save(self) -> None:
        def get_row() -> list:
            rd = []
            for col_name in self.data.columns:
                rd.append(self.data.rowdata[col_name])
            return rd

        try:
            if self.mode == 'append':
                LOGGER.debug("[Sheet {0}] Appending row: {1}".format(self.name, get_row()))
                self.ws.append_row(get_row())
            elif self.mode == 'insert':
                LOGGER.debug("[Sheet {0}] Inserting row at position {2}: {1}".format(self.name, get_row(), self.insert_at))
                self.ws.insert_row(get_row(), self.insert_at)

        except (gspread.UpdateCellError, gspread.RequestError) as e:
            LOGGER.error("Gspread failed - {}: {}".format(e.args[0], e.args[1]))


class Total(object):
    def __init__(self, data: dict):
        self.columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Total', 'AvgStay',
                        'FlnySent', 'FlnySentStay', 'MisdSent', 'MisdSentStay', 'FlnyUnsent', 'FlnyUnsentStay',
                        'MisdUnsent','MisdUnsentStay', 'Age18Less', 'Age18_24', 'Age25_34', 'Age35_44', 'Age45_54',
                        'Age55Plus']
        self.name = 'Total'
        self.rowdata = dict()
        for cl in self.columns:
            if cl in data:
                self.rowdata[cl] = data[cl]
        self.FlnySent(data)
        self.FlnySentStay(data)
        self.MisdSent(data)
        self.MisdSentStay(data)
        self.FlnyUnsent(data)
        self.FlnyUnsentStay(data)
        self.MisdUnsent(data)
        self.MisdUnsentStay(data)
        show("Data for Total: ", self.rowdata)

    def FlnySent(self, data: dict):
        self.rowdata['FlnySent'] = data['MenFlnySent'] + data['WmnFlnySent']

    def FlnySentStay(self, data: dict):
        m = data['MenFlnySent']
        ms = data['MenFlnySentStay']
        w = data['WmnFlnySent']
        ws = data['WmnFlnySentStay']
        self.rowdata['FlnySentStay'] = round((m * ms + w * ws) / (m + w))

    def MisdSent(self, data: dict):
        self.rowdata['MisdSent'] = data['MenMisdSent'] + data['WmnMisdSent']

    def MisdSentStay(self, data):
        m = data['MenMisdSent']
        ms = data['MenMisdSentStay']
        w = data['WmnMisdSent']
        ws = data['WmnMisdSentStay']
        self.rowdata['MisdSentStay'] = round((m * ms + w * ws) / (m + w))

    def FlnyUnsent(self, data: dict):
        self.rowdata['FlnyUnsent'] = data['MenFlnyUnsent'] + data['WmnFlnyUnsent']

    def FlnyUnsentStay(self, data: dict):
        m = data['MenFlnyUnsent']
        ms = data['MenFlnyUnsentStay']
        w = data['WmnFlnyUnsent']
        ws = data['WmnFlnyUnsentStay']
        self.rowdata['FlnyUnsentStay'] = round((m * ms + w * ws) / (m + w))

    def MisdUnsent(self, data: dict):
        self.rowdata['MisdUnsent'] = data['MenMisdUnsent'] + data['WmnMisdUnsent']

    def MisdUnsentStay(self, data: dict):
        m = data['MenMisdUnsent']
        ms = data['MenMisdUnsentStay']
        w = data['WmnMisdUnsent']
        ws = data['WmnMisdUnsentStay']
        self.rowdata['MisdUnsentStay'] = round((m * ms + w * ws) / (m + w))


class Men(object):
    def __init__(self, data: dict):
        self.columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Men', 'MAvgStay',
                        'MenFlnySent','MenFlnySentStay', 'MenMisdSent', 'MenMisdSentStay', 'MenFlnyUnsent',
                        'MenFlnyUnsentStay','MenMisdUnsent', 'MenMisdUnsentStay']
        self.name = 'Men'
        self.rowdata = dict()
        for cl in self.columns:
            if cl in data:
                self.rowdata[cl] = data[cl]
        self.AvgStay(data)
        show("Data for Men: ", self.rowdata)

    def AvgStay(self, data: dict):
        fs = data['MenFlnySent']
        fss = data['MenFlnySentStay']
        fu = data['MenFlnyUnsent']
        fus = data['MenFlnyUnsentStay']
        ms = data['MenMisdSent']
        mss = data['MenMisdSentStay']
        mu = data['MenMisdUnsent']
        mus = data['MenMisdUnsentStay']
        self.rowdata['MAvgStay'] = round((fs * fss + fu * fus + ms * mss + mu * mus) / (fs + fu + ms + mu))


class Women(object):
    def __init__(self, data: dict):
        self.columns = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Wmn', 'WAvgStay',
                        'WmnFlnySent', 'WmnFlnySentStay', 'WmnMisdSent', 'WmnMisdSentStay', 'WmnFlnyUnsent',
                        'WmnFlnyUnsentStay', 'WmnMisdUnsent', 'WmnMisdUnsentStay']
        self.name = 'Women'
        self.rowdata = dict()
        for cl in self.columns:
            if cl in data:
                self.rowdata[cl] = data[cl]
        self.AvgStay(data)
        show("Data for Women: ", self.rowdata)

    def AvgStay(self, data: dict):
        fs = data['WmnFlnySent']
        fss = data['WmnFlnySentStay']
        fu = data['WmnFlnyUnsent']
        fus = data['WmnFlnyUnsentStay']
        ms = data['WmnMisdSent']
        mss = data['WmnMisdSentStay']
        mu = data['WmnMisdUnsent']
        mus = data['WmnMisdUnsentStay']
        self.rowdata['WAvgStay'] = round((fs * fss + fu * fus + ms * mss + mu * mus) / (fs + fu + ms + mu))
