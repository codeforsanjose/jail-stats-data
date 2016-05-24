ROOT=/Users/james/Dropbox/Work/CodeForSanJose/JailStats
DEV=$(ROOT)/dev
PROD=$(ROOT)/prod
DOCKER=$(ROOT)/_docker


default: buildprod

buildprod:
    cp $(DEV)/*.py $(PROD)
