FROM postgres:9.5

MAINTAINER Jeremias Wong <jellyjellyrobot@gmail.com>

RUN sed --in-place 's/httpredir.debian.org/mirror.0x.sg/' /etc/apt/sources.list

RUN until apt-get update; \
  do echo "retrying update" ; \
  done;


# Configure Postgres

ENV POSTGRES_PASSWORD=NOT_THIS_PASSWORD
ENV POSTGRES_USER=NOT_THIS_USER
ENV POSTGRES_DB=TEST_DB

# COPY ./schema.sql /docker-entrypoint-initdb.d/

ADD create_hstore_extension.sh docker-entrypoint-initdb.d/create_hstore_extension.sh

EXPOSE 5432

