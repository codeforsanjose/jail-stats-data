ROOT=/Users/james/Dropbox/Work/CodeForSanJose/JailStats
DEV=$(ROOT)/dev

DOCKER=$(ROOT)/_docker
PROD_CAP=$(DOCKER)/capture
PROD_WEB=$(DOCKER)/web


default: buildprod

# Does not copy config.py!
buildprod:
	cp $(DEV)/*.py $(PROD_CAP)
	chmod 755 $(PROD_CAP)/capture.py
	cp $(DEV)/web.py $(PROD_WEB)
	chmod 755 $(PROD_WEB)/web.py

builddocker: buildprod
	-docker rmi  cfsj_js_cap_image
	docker build --rm -t cfsj_js_cap_image ./_docker
	docker images
	docker ps -a