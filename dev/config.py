#!/usr/bin/python3

import logging
import datetime
import os
import json
from types import MappingProxyType
from collections import ChainMap

from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()


email_fmt1 = '''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''

_prod_config = dict(
    database=dict(
        active=True,
        name='/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db',
    ),
    gspread=dict(
        active=True,
        name="SCC Daily Jail Stats",
        credentials_file='/Users/james/Dropbox/Development/.keys/Google/CFSJ/CFSJ-JailStats-4898258d3468.json',
        worksheets=['Total', 'Men', 'Women'],
        mode='insert',
        insert_at=4,
    ),
)

_test_config = dict(
    database=dict(
        active=True,
        name='/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats_test.db',
    ),
    gspread=dict(
        active=True,
        name="SCC Daily Jail Stats - Test",
        credentials_file='/Users/james/Dropbox/Development/.keys/Google/CFSJ/CFSJ-JailStats-4898258d3468.json',
        worksheets=['Total', 'Men', 'Women'],
        mode='insert',
        insert_at=4,
    ),
)


_base_config = dict(
    scheduler = dict(
        timezone = 'US/Pacific',
        schedule = dict(
            hour = 8,
        ),
    ),
    logs = dict(
        stdout = dict(
            active = True,
            level = logging.DEBUG,
            format = '[%(levelname) -8s %(asctime)s %(name)s:%(funcName)s:%(lineno)d)] %(message)s',
            datefmt = '%y-%m-%d %H:%M:%S',
        ),
        file = dict(
            active = True,
            level = logging.DEBUG,
            format = '[%(levelname) -8s %(asctime)s %(name)s:%(funcName)s:%(lineno)d)] %(message)s',
            datefmt = '%y-%m-%d %H:%M:%S',
            path = 'logs',
            filename = 'capture.log',
        ),
        email=dict(
            active=True,
            level=logging.ERROR,
            format=email_fmt1,
            datefmt=None,
            credentials_file='../_private/cfsj_monitor_gmail.json',
            handler = dict(
                mailhost=('smtp.gmail.com', 587),
                fromaddr='cfsj.monitor@gmail.com',
                toaddrs=['cfsj.test@gmail.com'],
                subject="Alarm: Jail Stats",
                credentials=(),
                secure=(),
            ),
        ),
    ),
    data_source = dict(
        url = 'https://www.sccgov.org/doc/Doc_daily_pop.pdf',
        retries = 10,
        retry_delay = 5,
        archive = True,
        archive_path = 'data',
        name_fmt = lambda suffix: "daily_pop_stats_{}.{}".format(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SUTC"), suffix),
        pdf_filename = lambda: _DATA_SOURCE()['name_fmt']('pdf') if _DATA_SOURCE()['archive'] else "current_data.pdf",
        text_filename = lambda: _DATA_SOURCE()['name_fmt']('txt') if _DATA_SOURCE()['archive'] else "current_data.txt",
        archive_pdf = lambda: os.path.join(_DATA_SOURCE()['archive_path'], _DATA_SOURCE()['pdf_filename']()),
        archive_text = lambda: os.path.join(_DATA_SOURCE()['archive_path'], _DATA_SOURCE()['text_filename']()),
    ),
)

_RUN_MODE = 'test'
_SCHEDULER = lambda: _scheduler
_DATA_SOURCE = lambda: _data_source
_DATABASE = lambda: _database
_LOGS = lambda x: _logs(x)
_GSPREAD = lambda: _gspread


def config_init(mode='test'):
    global _RUN_MODE, _CONFIG, _scheduler, _data_source, _database, _log_info, _logs, _gspread

    # Decode the JSON file containing the email credentials
    def object_decoder(obj):
        if '__type__' in obj and obj['__type__'] == 'credentials':
            return (obj['username'], obj['password'])
        return obj

    _RUN_MODE = mode
    show(_RUN_MODE)
    if _RUN_MODE == 'prod':
        _CONFIG = ChainMap(_prod_config, _base_config)
    else:
        _CONFIG = ChainMap(_test_config, _base_config)

    ecfg = _CONFIG['logs']['email']
    if ecfg['active']:
        with open(ecfg['credentials_file']) as data_file:
            data = json.load(data_file, object_hook=object_decoder)
            _CONFIG['logs']['email']['handler']['credentials'] = data
            pprint(ecfg)

    _scheduler = MappingProxyType(_CONFIG['scheduler'])
    _data_source = MappingProxyType(_CONFIG['data_source'])
    _database = MappingProxyType(_CONFIG['database'])
    _log_info = MappingProxyType(_CONFIG['logs'])
    _logs = lambda x: _log_info[x]
    _gspread = MappingProxyType(_CONFIG['gspread'])

    return

def run_tests():
    def print_var(x):
        print(("------------------ {0} ----------------".format(x)))
        pprint(eval(x))

    print("=====================================================================================")
    print("                                      DEBUG CONFIG")
    print("=====================================================================================")
    config_init('test')
    show(_CONFIG)
    SCHEDULER = _SCHEDULER()
    show(SCHEDULER)
    DATA_SOURCE = _DATA_SOURCE()
    show(DATA_SOURCE)
    DATABASE = _DATABASE()
    show(DATABASE)
    LOGS_STDOUT = _LOGS('stdout')
    show(LOGS_STDOUT)
    LOGS_FILE = _LOGS('file')
    show(LOGS_FILE)
    LOGS_EMAIL = _LOGS('email')
    show(LOGS_EMAIL)
    GSPREAD = _GSPREAD()
    show(GSPREAD)
    # print("==================================== ALL GLOBALS ===================================")

    print("\n\n=====================================================================================")
    print("                                      PROD CONFIG")
    print("=====================================================================================")
    config_init('prod')
    show(_CONFIG)
    SCHEDULER = _SCHEDULER()
    show(SCHEDULER)
    DATA_SOURCE = _DATA_SOURCE()
    show(DATA_SOURCE)
    DATABASE = _DATABASE()
    show(DATABASE)
    LOGS_STDOUT = _LOGS('stdout')
    show(LOGS_STDOUT)
    LOGS_FILE = _LOGS('file')
    show(LOGS_FILE)
    LOGS_EMAIL = _LOGS('email')
    show(LOGS_EMAIL)
    GSPREAD = _GSPREAD()
    show(GSPREAD)
    # print("==================================== ALL GLOBALS ===================================")

    return


def main():
    run_tests()


if __name__ == '__main__':
    main()
