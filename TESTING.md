# Testing

## Local Setup

We use boot2docker image for consistency. We shall set the docker environment variables with the following command.

```sh

# Set up local environment variables
eval $(docker-machine env local-dev)

# Rebuild
docker-compose up --build

# Teardown
docker-compose rm -f {CONTAINER NAME}

# Inspecting running container
docker exec -i -t $TARGET_CONTAINER /bin/bash

```

## Env file

Enviornmental variables are stored in _deployment/fetch.env.

### Facebook

You may find the relevant information at [Facebook Developers](https://developers.facebook.com/tools/accesstoken/)

```

#_deployment/fetch.env
FACEBOOK_ACCESS_TOKEN=******

```

### SSL

Please generate ssl certs in the format that nginx-proxy [requires](https://github.com/jwilder/nginx-proxy#ssl-support) and place them at .

## Test Cases

To be updated with automated test cases.

### RabbitMQ

```

# maxDepth
# Queues [fetch, parse]
{"maxDepth": 1}

# Facebook
# Queue [filter]
{"potential_leads": ["1443823632507167"], "protocol": "fb", "depth": 1}
{"potential_leads": ["420608754800233"], "protocol": "fb", "depth": 1}
{"potential_leads": ["10084673031"], "protocol": "fb", "depth": 1}
{"potential_leads": ["113901278620393"], "protocol": "fb", "depth": 1}
{"potential_leads": ["104958162837"], "protocol": "fb", "depth": 1}
{"potential_leads": ["128737643875635"], "protocol": "fb", "depth": 1}

# LinkedIn
# Queue [filter]
{"potential_leads": ["https://www.linkedin.com/company/cisco"], "protocol": "linkedin", "depth": 1}

# Foursquare
# Queue [filter]
{"potential_leads": ["4b7a6059f964a520002b2fe3"], "protocol": "fsquare", "depth": 1}

# Google
# Queue [filter]
{"potential_leads": ["ChIJyY4rtGcX2jERIKTarqz3AAQ"], "protocol": "google", "depth": 1}

```

### Backend API

```
curl -v http://backend.crawlz.me/api/maxDepth/1?api_key=******
curl -v http://backend.crawlz.me/api/search/jon%20stewart
curl -v http://backend.crawlz.me/api/search/intel
curl -v http://backend.crawlz.me/api/search/national%20university%20of%20singapore
curl -v http://backend.crawlz.me/api/search/mediacorp
curl -v http://backend.crawlz.me/api/search/nanyang%20technological%university
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
docker-machine ssh local-dev tce-load -wi htop
docker-machine scp -r _deployment/ssl local-dev:~/ssl

```

## Remote Deployment

Make sure that you have root access to the target machine and your ssh key is in authorized_keys. You may change the target ip-address to your preferred endpoint

```sh

docker-machine create --driver generic \
  --generic-ip-address $(dig +short crawlz.me | tail -n 1) \
  --generic-ssh-key $HOME/.ssh/id_rsa prod

```


## Make disk space great again!

```sh

# Delete all containers
docker rm $(docker ps -a -q)
# Delete all images
docker rmi $(docker images -q)

```
