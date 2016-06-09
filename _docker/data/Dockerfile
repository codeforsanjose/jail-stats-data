# JailStats Data

FROM cfsj_js_base
MAINTAINER JamesHaskell

WORKDIR /

RUN mkdir -p /__database/backup
RUN mkdir /__archives

COPY /jailstats.db /__database/
COPY /*.json /__database/
