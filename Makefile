ROOT=/Users/james/Dropbox/Work/CodeForSanJose/JailStats
DEV=$(ROOT)/dev

DOCKER=$(ROOT)/_docker
PROD_CAP=$(DOCKER)/capture
PROD_WEB=$(DOCKER)/web


default: buildprod

# Does not copy config.py!
buildprod:
	cp $(DEV)/archives.py $(PROD_CAP)
	cp $(DEV)/capture.py $(PROD_CAP)
	cp $(DEV)/config.py $(PROD_CAP)
	cp $(DEV)/logsetup.py $(PROD_CAP)
	cp $(DEV)/parse_pdf.py $(PROD_CAP)
	cp $(DEV)/spreadsheet.py $(PROD_CAP)
	chmod 755 $(PROD_CAP)/capture.py

	cp $(DEV)/web.py $(PROD_WEB)
	chmod 755 $(PROD_WEB)/web.py

buildprodall:
	cp $(DEV)/*.py $(PROD_CAP)
	cp $(DEV)/web.py $(PROD_WEB)
