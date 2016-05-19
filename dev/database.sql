-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile
/*
SQLite3 database
Name: jailstats.db

*/

-- Original create (approx 12 May 2016).
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


# 16 May 2016 - Add column for date, so we can log the "As Of" date and time.
ALTER TABLE main.daily ADD AsOfDate TEXT;


-- Build timestring
SELECT datetime(datetime('now'));

--
SELECT *, (Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00')  from daily;

-- Convert timestring to DATE
DATE(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00')
SELECT Year, Month, Day, datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00')  from daily;
SELECT *, datetime(datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00:00'))  from daily;

-- Julianday
SELECT *, strftime('%J', datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00'))  from daily;
SELECT *, julianday(datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00'))  from daily;

-- Unix time
SELECT *, strftime('%s', datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00'))  from daily;
SELECT *, (julianday(datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00')) - 2440587.5) * 86400.0  from daily;

-- Update the new column
UPDATE daily SET AsOfDate = round((julianday(datetime(Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || ' 05:00')) - 2440587.5) * 86400.0);

// ISO8601 date - NOTE: this is set to PDT!!!!
SELECT *, (Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || 'T05:00:00-07:00')  from daily;


/* --------------------- [2016.05.16 - Mon] ADDING 'AsOfDate' ------------------------------ */
ALTER TABLE main.daily RENAME TO daily1;

CREATE TABLE IF NOT EXISTS main.daily(
  Year INT,
  Month INT,
  Day INT,
  Hour INT,
  Minute INT,
  AsOfDate TEXT,
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
DROP INDEX daily_pk;
CREATE UNIQUE INDEX main.daily_pk ON daily(Year, Month, Day);


INSERT INTO main.daily
 SELECT
  Year,
  Month,
  Day,
  5,
  0,
  (Year || '-' || substr('0' || Month, -2) || '-' || substr('0' || Day, -2) || 'T05:00:00-07:00'),
  Total,
  AvgStay,

  Men,

  MenFlnySent,
  MenFlnySentStay,
  MenMisdSent,
  MenMisdSentStay,

  MenFlnyUnsent,
  MenFlnyUnsentStay,
  MenMisdUnsent,
  MenMisdUnsentStay,

  Wmn,

  WmnFlnySent,
  WmnFlnySentStay,
  WmnMisdSent,
  WmnMisdSentStay,

  WmnFlnyUnsent,
  WmnFlnyUnsentStay,
  WmnMisdUnsent,
  WmnMisdUnsentStay,

  Age18Less,
  Age18_24,
  Age25_34,
  Age35_44,
  Age45_54,
  Age55Plus
FROM main.daily1;



/* --------------------- [2016.05.18 - Wed] ADDING 'DayOfWeek' ------------------------------ */

DROP TABLE IF EXISTS daily1;
ALTER TABLE main.daily RENAME TO daily1;

CREATE TABLE IF NOT EXISTS main.daily(
  Year INT,
  Month INT,
  Day INT,
  Hour INT,
  Minute INT,
  DayOfWeek INT,
  AsOfDate TEXT,
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
DROP INDEX daily_pk;
CREATE UNIQUE INDEX main.daily_pk ON daily(Year, Month, Day);


INSERT INTO main.daily
 SELECT
  Year,
  Month,
  Day,
  Hour,
  Minute,
  strftime('%w', AsOfDate),
  AsOfDate,
  Total,
  AvgStay,

  Men,

  MenFlnySent,
  MenFlnySentStay,
  MenMisdSent,
  MenMisdSentStay,

  MenFlnyUnsent,
  MenFlnyUnsentStay,
  MenMisdUnsent,
  MenMisdUnsentStay,

  Wmn,

  WmnFlnySent,
  WmnFlnySentStay,
  WmnMisdSent,
  WmnMisdSentStay,

  WmnFlnyUnsent,
  WmnFlnyUnsentStay,
  WmnMisdUnsent,
  WmnMisdUnsentStay,

  Age18Less,
  Age18_24,
  Age25_34,
  Age35_44,
  Age45_54,
  Age55Plus
FROM main.daily1;

-- We are using ISO Weekdays (Mon=1, Sun=7)
UPDATE daily
  SET DayOfWeek = 7
  WHERE DayOfWeek = 0;