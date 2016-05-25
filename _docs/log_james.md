## To Do.todo


## Log

### 2016.05.25 - Wed

* Renamed files to "myxxx" to prevent any import confusion.
* Created mydb.py, with class DB.  Contains all the database code.
* In capture.py, moved all pdf download code into new class Download.
	* Replaced urlretrieve with urlopen, as per [here](http://stackoverflow.com/questions/32763720/timeout-a-file-download-with-python-urllib).
* Saved to GIT.
* Moved all PDF handling to mypdf.py, in new class: PDF.
* Saved to GIT.
* 

### 2016.05.24 - Tue

* Added "env" positional variable to argparse.  Defaults to "prod".  The debug switch and the environment are now separate.
* Test OK.
* Saved to GIT.
* Added Archive Maintainer - will delete old files every run cycle.
* Reorganized data and archive directories for easier deployment. 
* Test OK.
* Saved to GIT.
* Docker:
	* Tried using the frolvlad/alpine-python3 docker image... doesn't have SQLite, and there doesn't look to be an easy way to get it.  
	* Trying prolocutor/docker-python-sqlite...
	* 


### 2016.05.23 - Mon

* Added prod folder (will hold production Docker files).
* Revised Config.
* Loading into a Docker container:
	* Using container "frolvlad/alpine-python3" as the base.
	* The "show" package was not installing on the Docker alpine-python3 system (GCC missing).  Added override for "show" that supports all the show calls, but will use pprint.
	* See the Docker config notes for more details.

### 2016.05.21 - Sat

* Cleaned up of the Config system.  Config now uses a base (the production environment), but individual settings can be overridden in the test_config dictionary.
* Saved to GIT.
* Removed .gitignore file from repo.
* Saved to GIT.
* Stopped tracking .gitignore.
* Saved to GIT.

### 2016.05.20 - Fri

* Cleaned up config.

### 2016.05.19 - Thu

* Modified config to use a base config, and overrides for test vs. prod.  Don't like it... required globals to be exposed as lambda's.  More massaging needed...

### 2016.05.18 - Wed

* Spreadsheet code working.
* Uploaded all current data in SQLite DB to Spreadsheet.
* Created a public read-only link to the spreadsheet.

### 2016.05.16 - Mon

* Started Spreadsheet code.

### 2016.05.13 - Fri

* Downloading and parsing files working OK (capture.py).
* Simple REST web site working OK.
* Scheduler working well.
* Logging / error handling in place

### 2016.05.12 - Thu

* Downloading and parsing files working OK (capture.py).
* Simple REST web site working OK.
* Saved to GIT.

### 2016.05.11 - Wed

* Created JailStats project.  Started with the PDFlib TET example program: extractor.py.