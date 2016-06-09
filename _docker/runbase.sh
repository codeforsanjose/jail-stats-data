#!/bin/sh
docker run -it --rm  --name cfsj_js_capture \
	--volumes-from cfsj_js_data \
cfsj_js_base /bin/sh