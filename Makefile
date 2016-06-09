ROOT=/Users/james/Dropbox/Work/CodeForSanJose/JailStats
DEV=$(ROOT)/dev
DOCKER=$(ROOT)/_docker

PROD_CAP=$(DOCKER)/base
CAP_FILES=$(DEV)/capture.py $(DEV)/myarchives.py $(DEV)/myconfig.py $(DEV)/mydb.py $(DEV)/mylogsetup.py $(DEV)/mypdf.py $(DEV)/myspreadsheet.py 
CAP_TEST_FILES=$(DEV)/test/test.py
CRED_GSPREAD=/Users/james/Dropbox/Development/.keys/Google/CFSJ/CFSJ-JailStats-4898258d3468.json
CRED_EMAIL=$(ROOT)/_private/cfsj_monitor_gmail.json

PROD_DATA=$(DOCKER)/data
DATA_FILES=$(ROOT)/data/jailstats.db

PROD_WEB=$(DOCKER)/base/web
WEB_FILES=$(DEV)/web.py


default: all

# Does not copy config.py!
context:
	-rm $(PROD_CAP)/*.py
	-rm $(PROD_CAP)/test/*.py
	-rm $(PROD_CAP)/web/*.py

	cp $(CAP_FILES) $(PROD_CAP)
	cp $(CAP_TEST_FILES) $(PROD_CAP)/test
	chmod 755 $(PROD_CAP)/capture.py

	cp $(WEB_FILES) $(PROD_WEB)
	chmod 755 $(PROD_WEB)/web.py

	cp $(DATA_FILES) $(PROD_DATA)
	cp $(CRED_GSPREAD) $(PROD_DATA)/gspread.json
	cp $(CRED_EMAIL) $(PROD_DATA)/email.json


image_base: context
	-docker rmi  cfsj_js_base
	docker build --rm -t cfsj_js_base ./_docker/base

image_data: context image_base
	-docker rmi  cfsj_js_data
	docker build --rm -t cfsj_js_data ./_docker/data

image_web: context
	-docker rmi  cfsj_js_web
	docker build --rm -t cfsj_js_web ./_docker/web

all: context image_base image_data image_web
