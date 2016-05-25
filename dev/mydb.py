#!/usr/bin/python3
# SQLite DB processes for JailStats

import sqlite3 as lite
import logging

from pprint import pformat
from show import show

show.set(where=True)
show.set(fmtfunc=pformat)
show.prettyprint()
show.set(show=False)

LOGGER = logging.getLogger('capture')


class DB:
    column_names = ['Year', 'Month', 'Day', 'Hour', 'Minute', 'DayOfWeek', 'AsOfDate', 'Total', 'AvgStay', 'Men',
                    'MenFlnySent', 'MenFlnySentStay', 'MenMisdSent', 'MenMisdSentStay', 'MenFlnyUnsent',
                    'MenFlnyUnsentStay', 'MenMisdUnsent', 'MenMisdUnsentStay', 'Wmn', 'WmnFlnySent', 'WmnFlnySentStay',
                    'WmnMisdSent', 'WmnMisdSentStay', 'WmnFlnyUnsent', 'WmnFlnyUnsentStay', 'WmnMisdUnsent',
                    'WmnMisdUnsentStay', 'Age18Less', 'Age18_24', 'Age25_34', 'Age35_44', 'Age45_54', 'Age55Plus']

    def __init__(self, active=False, name=''):
        self.active = active
        self.name = name

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
