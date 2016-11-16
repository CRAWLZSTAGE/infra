# Testing

## Local Setup

We use boot2docker image for consistency. We shall set the docker environment variables with the following command.

```sh

# Local Deployment
eval $(docker-machine env local-dev)

docker-compose up

```


## Local Deployment

```sh

docker-machine create --driver virtualbox \
  --virtualbox-memory=4096 \
  --virtualbox-cpu-count=4 \
  --virtualbox-disk-size=20480 \
  --virtualbox-no-share \
  local-dev

docker-machine ssh local-dev sudo mkdir -p /mnt/sda1/ext

```


