# Docker Configuration

## Overview
Two images are required:
1. Data and files - this is a data only volume container, used to persist the database (including database backups) and downloaded PDF and conversion archive files.
2. Python3 program files.  This is the Base container... the Data container is build using this image.  Both the "scraper" and the REST web site are run with this image.

## The Plan

1. Create the Base docker container. 
2. Create the Data container.  This is the Base container, with an extra "data" directory containing subdirectories for the database and backups, and for the PDF and conversion archives.
3. Run the App:
	* Upload and run the Data container (it runs and exits).
	* Upload the Base container, and start crond.
	* Upload the Web container, and run it.

## Work

### Notes

* 

#### Build Commands

Run from `/Users/james/Dropbox/Work/CodeForSanJose/JailStats`.

|Task|Command|
|----|---|
|Rebuild the Base container|`make`|
|Run the Base container|`docker run -it cfsj_js_cap_image /bin/sh`|
|Run cron in the Base container|`crond -d 6 -f`|



### ToDo.todo

* Test crond running a Python program (test.py).  Use the "cronrun" shell script to run the program. @done(2016-06-07)
* Create "test" subdir of the capture @done(2016-06-08)
* Create the Data container.
* 

### Makefile

The Makefile (in the project root) will build the Docker Code Container.  The Code Container is considered the base image, and is used as the Data Container.

## Images

To build ALL images:  

	cd /Users/james/Dropbox/Work/CodeForSanJose/JailStats
	make

## Base Image

|Task|How To|
|----|----|
|Build


## Data Image


## Web Server Image

## Cron Setup

Following loosely these links: [Running cron](https://github.com/gliderlabs/docker-alpine/issues/120), [BusyBox cron container example](https://gist.github.com/andyshinn/3ae01fa13cb64c9d36e7).

* Create a shell script file, and put in the build context.
* Modify the existing cron file:
	* Run the Docker image
	* Copy the existing cron file at `/var/spool/cron/crontabs/root`.
	* Add the new schedule, referencing the shell script above.
* In the Dockerfile:
	* COPY the shell script file into the container.
	* COPY the "root" cron file back to `/var/spool/cron/crontabs/`.
	* Make the shell script executable in the container:
		* `RUN chmod +x /bin/<the shell script>`
	* Cron can be started to run in the foreground:
		* `CMD crond -d 6 -f`

* Example Dockerfile (note: running crond at level 2 will print a lot of debug info.  Run "cron --help" :  

        FROM gliderlabs/alpine:3.3
        COPY myawesomescript /bin/myawesomescript
        COPY root /var/spool/cron/crontabs/root
        RUN chmod +x /bin/myawesomescript
        CMD crond -d 6 -f

#### crond Logging Levels

|Lev|Description|
|---|---|
|0-4|Levels 0 through 4 appear to be the same.  Lots of cron details.|
|5|Shows some job details (user, pid and cmd) each execution.  When directing logging to stderr (the "-d" option), level 5 will show a lot of extraneous unintelligible info - use level 6 instead|
|6-9|Shows some job details (user, pid and cmd) each execution.  Seems to work well with either the "-l" or "-d" options.|

* See [here](https://busybox.net/downloads/BusyBox.html) for crond options.  
* Use the "-d" option to redirect cron logging to stderr.



## Old Work

### Configuration - Ubuntu
Using full Ubuntu / Python image from [DockerHub / Python](https://hub.docker.com/_/python/).

#### Data Container

From the _docker directory:
	
	docker run --name cfsj_js_data \
	   -v /usr/src/app/data \
	   -v /usr/src/app/archive \
	   cfsj_js_cap_image /bin/true 

	docker cp ../data/jailstats.db cfsj_js_data:usr/src/app/data
	docker cp ../archive cfsj_js_data:/usr/src/app

Check:
	docker run -it --rm --name cfsj-js \
		cfsj_js_cap_image /bin/sh
		
	docker run -it --rm --name cfsj-js \
		--volumes-from cfsj_js_data \
		cfsj_js_cap_image /bin/sh


### Code Container :

From the _docker directory:
	
	docker run -it --name cfsj_js \
	   --volumes-from cfsj_js_data \
	   prolocutor/docker-python-sqlite /bin/sh
	
	pip install --upgrade pip
	pip install apscheduler
	pip install argparse
	pip install gspread
	pip install oauth2client
	pip install pytz

	docker cp ../prod cfsj_js:source

To save the image:


To run a command line
	
## Configuration - Alpine
Using full Ubuntu / Python image from [DockerHub / docker-python-sqlite](https://hub.docker.com/r/prolocutor/docker-python-sqlite/).


### Data Container

From the _docker directory:
	
	docker run --name cfsj_js_data \
	   -v /data \
	   -v /archive \
	   prolocutor/docker-python-sqlite /bin/true 

	docker cp ../dev/data/jailstats.db cfsj_js_data:usr/src/app/data
	docker cp ../dev/archive cfsj_js_data:/

### Code Container :

From the _docker directory:
	
	docker run -it --name cfsj_js \
	   --volumes-from cfsj_js_data \
	   prolocutor/docker-python-sqlite /bin/sh
	
	pip install --upgrade pip
	pip install apscheduler
	pip install argparse
	pip install gspread
	pip install oauth2client
	pip install pytz

	docker cp ../prod cfsj_js:source

### Check it...
docker run -it --name cfsj_js \
	--volumes-from cfsj_js_data \
	frolvlad/alpine-python3 /bin/sh



### Commit
docker commit cfsj_js_data_source cfsj_data_image

### Check the image
docker run -itrm cfsj_data_image /bin/sh

### Delete the container
docker rm cfsj_js_data_source


### Container to copy the local files to a new managed volume
docker run --rm --name cfsj_js_data \
	-v /data \
	cfsj_data_image /bin/sh -c 'cp /data_source/jailstats.db /data'

### Check it...
docker run -it --rm --name cfsj_js \
	--volumes-from cfsj_js_data \
	frolvlad/alpine-python3 /bin/sh

### Remove the image
docker rmi cfsj_data_image





docker run --name cfsj_js_data \
	-v /Users/james/Dropbox/Work/CodeForSanJose/JailStats/dev:/data_source \
	-v /data \
	frolvlad/alpine-python3 /bin/sh -c 'cp /data_source/jailstats.db /data'

