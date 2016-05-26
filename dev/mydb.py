#!/usr/bin/python3
# SQLite DB processes for JailStats

import sqlite3 as lite
import time
import os
import datetime
import logging
from subprocess import call

from pprint import pformat
from show import show
from myarchives import clean_dir

show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()
show.set(show=False)

LOGGER = logging.getLogger('capture')

filename_dated = lambda base, ext: "{}_{}.{}".format(base,
                                                     datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SUTC"),
                                                     ext)
backup_ext = "bak"

class DB:
    column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Total', 'AvgStay', 'Men',
                    'MenFlnySent', 'MenFlnySentStay', 'MenMisdSent', 'MenMisdSentStay', 'MenFlnyUnsent',
                    'MenFlnyUnsentStay', 'MenMisdUnsent', 'MenMisdUnsentStay', 'Wmn', 'WmnFlnySent', 'WmnFlnySentStay',
                    'WmnMisdSent', 'WmnMisdSentStay', 'WmnFlnyUnsent', 'WmnFlnyUnsentStay', 'WmnMisdUnsent',
                    'WmnMisdUnsentStay', 'Age18Less', 'Age18_24', 'Age25_34', 'Age35_44', 'Age45_54', 'Age55Plus']

    def __init__(self, active: bool = False, name: str = '', backup_active: bool = False, backup_dir: str = '',
                 backup_retain_days: int = 21) -> None:
        self.active = active
        self.name = name
        self.backup_active = backup_active
        self.backup_dir = backup_dir
        self.backup_retain_days = backup_retain_days
        self.build_paths()
        show(self.__dict__, show=True)

    def build_paths(self):
        # Full path and filename for data
        self.path, self.filename = os.path.split(os.path.abspath(self.name))

        # BACKUP.
        if not self.backup_dir[0] == '/':
            self.backup_dir = os.path.split(os.path.join(self.path, self.backup_dir, "xxx"))[0]
        # Does the backup directory exist?
        if not os.path.exists(self.backup_dir):
            os.mkdir(self.backup_dir)

    def save(self, data: dict) -> None:
        if not self.active:
            LOGGER.warning("Data not saved to the Database - configured as inactive!")
            return

        conn = None
        try:
            LOGGER.debug("Saving data to database: {}".format(self.name))
            conn = lite.connect(self.name)
            with conn:
                conn.execute(
                    "INSERT INTO daily VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    [data['Year'],
                     data['Month'],
                     data['Day'],
                     data['Hour'],
                     data['Minute'],
                     data['DayOfWeek'],
                     data['AsOfDate'],
                     data['Total'],
                     data['AvgStay'],
                     data['Men'],
                     data['MenFlnySent'],
                     data['MenFlnySentStay'],
                     data['MenMisdSent'],
                     data['MenMisdSentStay'],

                     data['MenFlnyUnsent'],
                     data['MenFlnyUnsentStay'],
                     data['MenMisdUnsent'],
                     data['MenMisdUnsentStay'],

                     data['Wmn'],

                     data['WmnFlnySent'],
                     data['WmnFlnySentStay'],
                     data['WmnMisdSent'],
                     data['WmnMisdSentStay'],

                     data['WmnFlnyUnsent'],
                     data['WmnFlnyUnsentStay'],
                     data['WmnMisdUnsent'],
                     data['WmnMisdUnsentStay'],

                     data['Age18Less'],
                     data['Age18_24'],
                     data['Age25_34'],
                     data['Age35_44'],
                     data['Age45_54'],
                     data['Age55Plus']]
                    )
                LOGGER.info("Saved to database...")

        except lite.IntegrityError:
            LOGGER.warning("The data is already in the database!")

        except Exception as e:
            LOGGER.exception("save_to_db() failed:")

        finally:
            conn.close()

    def fetchall(self) -> list:
        if not self.active:
            LOGGER.error("Cannot fetch data - database is inactive!")
            return

        conn = None
        try:
            LOGGER.debug("Fetching all rows from database: {}".format(self.name))
            conn = lite.connect(self.name)
            cur = conn.cursor()
            with conn:
                cur.execute('SELECT * FROM daily ORDER BY AsOfDate ASC')
                all_rows = cur.fetchall()

        except Exception as e:
            LOGGER.exception("Unable to retrieve data from the database.")

        conn.close()
        return all_rows

    def maintain(self) -> None:
        self.backup()
        clean_dir(dir_path = self.backup_dir,
                       days = self.backup_retain_days,
                       prefixes = [os.path.splitext(self.filename)[0]],
                       suffixes = [backup_ext])

    def backup(self) -> None:
        if not self.backup_active:
            LOGGER.warning("Database maintenance note performed - DB configured as inactive!")
            return

        b_target = os.path.join(self.backup_dir, filename_dated(os.path.splitext(self.filename)[0], backup_ext))

        # Run the backup command
        command = "sqlite3 {} .dump > {}".format(self.name, b_target)
        show(self.__dict__, b_target, command, show=True)
        call(command, shell=True)
        LOGGER.info("Database backed up to: {}".format(b_target))


