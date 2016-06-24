ROOT=/Users/james/Dropbox/Work/CodeForSanJose/JailStats
DEV=$(ROOT)/dev
DOCKER=$(ROOT)/_docker

PROD_CAP=$(DOCKER)/capture
CAP_FILES=$(DEV)/capture.py $(DEV)/myarchives.py $(DEV)/mydb.py $(DEV)/mylogsetup.py $(DEV)/mypdf.py $(DEV)/myspreadsheet.py 

CAP_TEST_FILES=$(DEV)/test/test.py

CRED_GSPREAD=/Users/james/Dropbox/Development/.keys/Google/CFSJ/CFSJ-JailStats-4898258d3468.json
CRED_EMAIL=$(ROOT)/_private/cfsj_monitor_gmail.json

PROD_DATA=$(DOCKER)/data
DATA_FILES=$(ROOT)/data/jailstats.db

PROD_WEB=$(DOCKER)/web
WEB_FILES=$(DEV)/web.py


default: all

# Does not copy myconfig.py!
context:
	-rm $(PROD_CAP)/*.py
	-rm $(PROD_CAP)/test/*.py
	-rm $(PROD_DATA)/*
	-rm $(PROD_WEB)/*.py

	cp $(CAP_FILES) $(PROD_CAP)
	cp $(CAP_TEST_FILES) $(PROD_CAP)/test
	chmod 755 $(PROD_CAP)/capture.py

	cp $(WEB_FILES) $(PROD_WEB)
	chmod 755 $(PROD_WEB)/web.py

	cp $(DATA_FILES) $(PROD_DATA)
	cp $(CRED_GSPREAD) $(PROD_DATA)/gspread.json
	cp $(CRED_EMAIL) $(PROD_DATA)/email.json

image_capture: context
	-docker volume rm cfsj_js_data
	docker volume create --name cfsj_js_data
	-docker rmi  cfsj_js_capture
	docker build -f ./_docker/Docker-capture --rm -t cfsj_js_capture ./_docker

image_web: context
	-docker rmi  cfsj_js_web
	docker build -f ./_docker/Docker-web --rm -t cfsj_js_web ./_docker

all: context image_capture image_web
