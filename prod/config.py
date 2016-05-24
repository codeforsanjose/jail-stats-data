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
show.set(show=True)

'''
The configuration uses a base configuration (prod_config), and optional overrides.  The base config, "prod_config",
will be active if the environment is set to "prod" (the default).  If the program is run in debug mode (using the
"-d" command line option), then the environment will be set to "test".  The test_config dict must have the same
structure as prod_config, but need only contain the items to be overridden.  In other words, the base prod_config
is used for all configuration settings, and individual settings can be overridden in the test_config.
'''

email_fmt1 = '''
Message type:       %(levelname)s
Location:           %(pathname)s:%(lineno)d
Module:             %(module)s
Function:           %(funcName)s
Time:               %(asctime)s

Message:

%(message)s
'''

# Docker Production Config
prod_config = dict(
    scheduler = dict(
        timezone = 'US/Pacific',
        schedule = dict(
            hour = 8,
        ),
    ),
    logs = dict(
        stdout = dict(
            active = True,
            level = logging.WARNING,
            format = '[%(levelname) -8s %(asctime)s %(name)s:%(funcName)s:%(lineno)d)] %(message)s',
            datefmt = '%y-%m-%d %H:%M:%S',
        ),
        file = dict(
            active = False,
            level = logging.ERROR,
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
        archive_path = 'archive',
        name_fmt = lambda suffix: "daily_pop_stats_{}.{}".format(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SUTC"), suffix),
        pdf_filename = lambda: _DATA_SOURCE['name_fmt']('pdf') if _DATA_SOURCE['archive'] else "current_data.pdf",
        text_filename = lambda: _DATA_SOURCE['name_fmt']('txt') if _DATA_SOURCE['archive'] else "current_data.txt",
        archive_pdf = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['pdf_filename']()),
        archive_text = lambda: os.path.join(_DATA_SOURCE['archive_path'], _DATA_SOURCE['text_filename']()),
    ),
    database=dict(
        active=True,
        name='/data/jailstats.db',
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

# Non-Docker Local "Production" Config
prod_local_config = dict(
    logs = dict(
        stdout = dict(
            level = logging.DEBUG,
        ),
        file = dict(
            level = logging.DEBUG,
        ),
        email=dict(
            level=logging.ERROR,
        ),
    ),
    database=dict(
        name='/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/data/jailstats.db',
    ),
    gspread=dict(
        name="SCC Daily Jail Stats",
    ),
)

# Test Config
test_config = dict(
    logs = dict(
        stdout = dict(
            level = logging.DEBUG,
        ),
        file = dict(
            level = logging.DEBUG,
        ),
        email=dict(
            level=logging.ERROR,
        ),
    ),
    database=dict(
        active=True,
        name='/Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev/data/jailstats_test.db',
    ),
    gspread=dict(
        active=True,
        name="SCC Daily Jail Stats - Test",
    ),
)

_config_built = False


def build(env):
    if env == 'prod':
        config = prod_config
    else:
        config = dict()
        if env == 'test':
            override_config(prod_config, test_config, config)
        elif env == 'ptest':
            override_config(prod_config, prod_local_config, config)
    return config


def override_config(base, override, target):
    # show(base, override, "\n")
    if not (type(base) in (dict, ChainMap) and type(override) == dict):
        return

    base_keys = set(base.keys())
    override_keys = base_keys & set(override.keys())
    # show(base_keys, override_keys, "\n")
    for k in override_keys:
        if isinstance(base[k], dict):
            target[k] = ChainMap(override[k], base[k])
            # show(k, base[k], override[k], "\n")
            override_config(base[k], override[k], target[k])
    for k in (base_keys - override_keys):
        target[k] = base[k]


def config_init(env='prod'):
    global _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD, _config_built
    if env not in ['test', 'prod', 'ptest']:
        raise

    config = build(env)

    # Decode the JSON file containing the email credentials
    def object_decoder(obj):
        if '__type__' in obj and obj['__type__'] == 'credentials':
            return (obj['username'], obj['password'])
        return obj

    ecfg = config['logs']['email']
    if ecfg['active']:
        with open(ecfg['credentials_file']) as data_file:
            data = json.load(data_file, object_hook=object_decoder)
            config['logs']['email']['handler']['credentials'] = data

    _SCHEDULER = MappingProxyType(config['scheduler'])
    _DATA_SOURCE = MappingProxyType(config['data_source'])
    _DATABASE = MappingProxyType(config['database'])
    _LOGS = MappingProxyType(config['logs'])
    _GSPREAD = MappingProxyType(config['gspread'])

    _config_built = True
    show_config(env, _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD)
    return _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD


def get_config():
    global _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD, _config_built
    if not _config_built:
        raise
    return _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD


def show_config(title, scheduler, data_source, database, logs, gspread):
    print(
    "\n\n============================================================================================================")
    print("                                      Environment: {}".format(title))
    print(
    "============================================================================================================")
    show(scheduler)
    show(data_source)
    show(database)
    show(logs)
    show(gspread)
    print("-------- Overrides -------------------")
    show(_DATABASE['active'], _DATABASE['name'])
    show(_GSPREAD['active'], _GSPREAD['name'])
    show(_LOGS['stdout']['level'], _LOGS['file']['level'], _LOGS['email']['level'])
    print(
    "============================================================================================================\n\n")


def run_checks():
    global _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD

    def print_var(x):
        print(("------------------ {0} ----------------".format(x)))
        pprint(eval(x))

    env = 'test'
    scheduler, data_source, database, logs, gspread = config_init(env)
    show_config(env, scheduler, data_source, database, logs, gspread)
    # show_dicts(env, _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD)
    # scheduler1, data_source1, database1, logs1, gspread1 = config_init(env)
    # show_dicts(env, scheduler1, data_source1, database1, logs1, gspread1)

    env = 'ptest'
    _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD = config_init(env)
    show_config(env, _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD)

    env = 'prod'
    _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD = config_init(env)
    show_config(env, _SCHEDULER, _DATA_SOURCE, _DATABASE, _LOGS, _GSPREAD)

    return


def main():
    run_checks()


if __name__ == '__main__':
    main()
