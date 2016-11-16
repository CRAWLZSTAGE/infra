## COMMON_INIT_START

FROM debian:jessie

MAINTAINER Jeremias Wong <jellyjellyrobot@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

# For local development, Andrew's mirror is better
RUN sed --in-place 's/httpredir.debian.org/mirror.0x.sg/' /etc/apt/sources.list

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

COPY requirements.txt /
COPY parser.py /

RUN pip install -r requirements.txt

CMD ["python", "parser.py"]