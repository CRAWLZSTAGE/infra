## COMMON_INIT_START

FROM debian:jessie

MAINTAINER Jeremias Wong <jellyjellyrobot@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=linux
ENV TERMINFO=/etc/terminfo

# For local development, Andrew's mirror is better
RUN sed --in-place 's/deb.debian.org/mirror.0x.sg/' /etc/apt/sources.list

RUN until apt-get update; \
  do echo "retrying update"; \
  done;

RUN until apt-get install \
  -y --no-install-recommends \
    apt-utils; \
  do echo "install apt-utils"; \
  done;

RUN until apt-get upgrade -y; \
  do echo "retrying upgrade"; \
  done;

RUN until apt-get install \
  -y --no-install-recommends \
    nano \
    net-tools; \
  do echo "installing tools"; \
  done;

RUN until apt-get install \
  -y --no-install-recommends \
    libpq-dev \
    gcc \
    python-dev \
    python-pip \
    curl \
    python; \
  do echo "retrying install"; \
  done;

RUN curl https://bootstrap.pypa.io/get-pip.py | python

## COMMON_INIT_END

ENV MQTT_HOST=mqtt
ENV MQTT_USER=NOT_THIS_USER
ENV MQTT_PASSWORD=NOT_THIS_PASSWORD
ENV FACEBOOK_ACCESS_TOKEN=NOT_THIS_TOKEN
ENV MAX_DEPTH=5

COPY requirements.txt /

RUN pip install -r requirements.txt
COPY fetch.py /

CMD ["python", "fetch.py"]