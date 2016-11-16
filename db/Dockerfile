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
ENV PGDATA=/mnt/sda1/ext

# ./schema.sql /schmea.sql
# COPY ./schema.sql /docker-entrypoint-initdb.d/

EXPOSE 5432

