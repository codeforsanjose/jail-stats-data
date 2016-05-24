# Docker Configuration

## Overview
Two images are required:
1. Data and files - this is a data only volume container, used to persist the database and downloaded files.
2. Python3 program files.


## Configuration - Ubuntu
Using full Ubuntu / Python image from [DockerHub / Python](https://hub.docker.com/_/python/).

### Data Container

From the _docker directory:
	
	docker run --name cfsj_js_data \
	   -v /usr/src/app/data \
	   -v /usr/src/app/archive \
	   cfsj_js_cap_image /bin/true 

	docker cp ../data/jailstats.db cfsj_js_data:usr/src/app/data
	docker cp ../archive cfsj_js_data:/usr/src/app

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

