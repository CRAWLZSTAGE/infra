#Deployment

## Introduction

## Build and Push Images


Follow the instructions as [adapted.](https://docs.docker.com/engine/getstarted/step_six/)

```
docker login
docker build ./
docker tag $(docker image ls -q | head -n 1) crawlz*:latest



```
