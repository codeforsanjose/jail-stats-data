# Docker Configuration

## Overview
Two images are required:
1. Data and files - this is a data only volume container, used to persist the database and downloaded files.
2. Python3 program files.

## Configuration

### Database Container

	docker run --name cfsj_js_data \
	   -v /data \
	   frolvlad/alpine-python3 /bin/true 

	docker cp ../jailstats.db cfsj_js_data:data

### Code Container :
	
	docker run -it --name cfsj_js \
	   --volumes-from cfsj_js_data \
	   frolvlad/alpine-python3 /bin/sh
	
	pip install --upgrade pip
	pip install apscheduler
	pip install argparse
	pip install gspread
	pip install oauth2client
	pip install pytz

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

