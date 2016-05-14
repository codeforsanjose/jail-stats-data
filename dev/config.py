#!/usr/bin/python3

import logging, datetime, os, json
from pprint import pprint, pformat
from show import show
show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()

debug = False

_RUN_MODE = 'test'

email_fmt1 = '''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''

_CONFIG_ALL = dict(
    test = dict(
        instrumentation = dict(
            general = True,
            scheduler_active=True,
        ),
        scheduler = dict(
            timezone = 'US/Pacific',
            schedule = dict(
                hour = 7,
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
                credentials_file='../_private/cfsj_test_gmail.json',
                filename='capture.log',
            ),
        ),
        data_source = dict(
            url = 'https://www.sccgov.org/doc/Doc_daily_pop.pdf',
            retries = 10,
            retry_delay = 5,
            archive = True,
            archive_path = 'data',
            name_fmt = lambda suffix: "daily_pop_stats_{}.{}".format(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%_SUTC"), suffix),
            pdf_filename = lambda: _DATA_SOURCE['name_fmt']('pdf') if _DATA_SOURCE['archive'] else "current_data.pdf",
            text_filename = lambda: _DATA_SOURCE['name_fmt']('txt') if _DATA_SOURCE['archive'] else "current_data.txt",
            archive_pdf = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['pdf_filename']()),
            archive_text = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['text_filename']()),
        ),
        database = dict(
            active = True,
            name = "/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db",
        ),
    ),
    prod = dict(
        instrumentation = dict(
            general = True,
            scheduler_active=True,
        ),
        scheduler = dict(
            timezone = 'US/Pacific',
            schedule = dict(
                hour = 7,
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
                # format = '%(levelname) -8s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s',
                format = '[%(levelname) -8s %(asctime)s %(name)s:%(funcName)s:%(lineno)d)] %(message)s',
                datefmt = '%y-%m-%d %H:%M:%S',
                path = 'logs',
                filename = 'capture.log',
            ),
        ),
        data_source = dict(
            url = 'https://www.sccgov.org/doc/Doc_daily_pop.pdf',
            retries = 10,
            retry_delay = 5,
            archive = True,
            archive_path = 'data',
            name_fmt = lambda suffix: "daily_pop_stats_{}.{}".format(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%_SUTC"), suffix),
            pdf_filename = lambda: _DATA_SOURCE['name_fmt']('pdf') if _DATA_SOURCE['archive'] else "current_data.pdf",
            text_filename = lambda: _DATA_SOURCE['name_fmt']('txt') if _DATA_SOURCE['archive'] else "current_data.txt",
            archive_pdf = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['pdf_filename']()),
            archive_text = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['text_filename']()),
        ),
        database = dict(
            active = True,
            name = "/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/jailstats.db",
        ),
    ),
)

_CONFIG = _CONFIG_ALL[_RUN_MODE]
_SCHEDULER = _CONFIG['scheduler']
_DEBUG = _CONFIG['instrumentation']
_DEBUG_G = _CONFIG['instrumentation']['general']
_DATA_SOURCE = _CONFIG['data_source']
_DATABASE = _CONFIG['database']
_LOGS = _CONFIG['logs']

def config_init():
    # Read the email credentials
    def object_decoder(obj):
        if '__type__' in obj and obj['__type__'] == 'credentials':
            return (obj['username'], obj['password'])
        return obj

    ecfg = _LOGS['email']
    if ecfg['active']:
        with open(ecfg['credentials_file']) as data_file:
            data = json.load(data_file, object_hook=object_decoder)
            ecfg['credentials'] = data
            pprint(ecfg)
    return

def run_tests():
    debug = _DEBUG_G

    def print_var(x):
        print(("------------------ {0} ----------------".format(x)))
        pprint(eval(x))

    print_var('_CONFIG')
    print_var('_DEBUG')
    print_var('_DEBUG_G')
    print_var('_DATA_SOURCE')
    print("==================================== ALL GLOBALS ===================================")
    pprint(globals())
    return


def main():
    config_init()
    run_tests()


if __name__ == '__main__':
    main()