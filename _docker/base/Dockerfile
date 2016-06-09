# JailStats Update Program

FROM prolocutor/docker-python-sqlite
MAINTAINER JamesHaskell

WORKDIR /

# Capture
COPY *.py /_capture/
COPY *.sh /_capture/
COPY requirements.txt /_capture/
COPY test/test.py /_capture/test/

# Web
COPY web/*.py /_web/
COPY web/*.sh /_web/

# Cron
COPY cron/root /var/spool/cron/crontabs/root
RUN chmod +x /_capture/run.sh

RUN pip install -r /_capture/requirements.txt

# The following will run cron, with cron log output directed to stderr.
CMD crond -d 6 -f