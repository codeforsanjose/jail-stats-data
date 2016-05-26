## Description
Cumulative SCC Jail Statistics appears to be unavailable from the Santa Clara County Sheriff's Dept.  This program will scrape the SCC Sheriff's daily statistics at https://www.sccgov.org/doc/Doc_daily_pop.pdf, save the data to a database accessible via a REST interface, and push the data to a Google Spreadsheet at https://docs.google.com/spreadsheets/d/1VBP3rU1bEoclMwUJaI076UvP0tWosy9I_5G5bPn28Vs/edit?usp=sharing.

## Current Status
As of 26 May 2016:
There are two executable components

### Scraping Program

#### Configuration

* Fully configurable directories, DB location, etc., with the myconfig.py file.
* Base production configuration, with overrideable configuration sets (for testing, local deployment, Docker deployment, etc.).
* The Scraper is currently configured to run every day at 8AM PST.
* If a download fails, it will be reattempted 10 times, starting with a 5 second delay.  The delay period will be doubled each re-attempt.

#### Maintenance

* Backups of the SQLite3 DB are taken each download cycle.
* Backups older than a specified number of days will be automatically deleted.
* Downloaded PDF's and text conversion files are archived.
* Archived PDF and text files older than a specified number of days will be automatically deleted.

#### Google Spreadsheet

* The spreadsheets are configured in myspreadsheets.py.

#### Credentials

* All credentials (e.g. for Google Sheets, email logging, etc) are read from text files.  The location of the text files is specifed in myconfig.py, but these files are not part of the git repo.

### Deployment

For now, the Scraper is running on a personal machine.   

The Scraping program and a simple REST Web interface will be deployed using Docker, probably on Google Container Engine.  This should be completed by mid-June.  

The planned deployment will be based on the `prolocutor/docker-python-sqlite` Alpine image, with the necessary Python libs pip'd, and program files copied.  Persistent data (database, archives, DB backups) will be stored in a separate data volume container, based on the same image as above.
