#!/bin/sh
docker run -it --rm \
	-v cfsj_js_data:/__data \
	cfsj_js_capture /_capture/start.sh