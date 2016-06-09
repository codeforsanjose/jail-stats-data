#!/bin/sh
docker run -it --name cfsj_js_data \
	-v /__database \
	-v /__archives \
cfsj_js_data /bin/true