# Testing

## Local Setup

We use boot2docker image for consistency. We shall set the docker environment variables with the following command.

```sh

# Local Deployment
eval $(docker-machine env local-dev)

docker compose build
docker-compose up

# Teardown
docker-compose rm

```

## Env file

Enviornmental variables are stored in _deployment. The files and expected 

```

#_deployment/fetch.env
FACEBOOK_ACCESS_TOKEN=******
## https://developers.facebook.com/tools/accesstoken/
'{"potential_leads": ["420608754800233"], "protocol": "fb", "depth": 1}'

```


## Local Deployment

```sh

docker-machine create --driver virtualbox \
  --virtualbox-memory=4096 \
  --virtualbox-cpu-count=4 \
  --virtualbox-disk-size=20480 \
  --virtualbox-no-share \
  local-dev

eval $(docker-machine env local-dev)
docker-machine ssh local-dev sudo mkdir -p /mnt/sda1/ext

```

## Remote Deployment

```sh

```


## Make disk space great again!

```sh
# Delete all containers
docker rm $(docker ps -a -q)
# Delete all images
docker rmi $(docker images -q)
```
