# CRAWLZ.me

[![MIT License](https://img.shields.io/npm/l/stack-overflow-copy-paste.svg?style=flat-square)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/CRAWLZSTAGE/infra.svg?branch=master)](https://travis-ci.org/CRAWLZSTAGE/infra)
[![Code Climate](https://codeclimate.com/github/CRAWLZSTAGE/infra/badges/gpa.svg)](https://codeclimate.com/github/CRAWLZSTAGE/infra)
[![Coverage Status](https://coveralls.io/repos/github/CRAWLZSTAGE/infra/badge.svg?branch=benj)](https://coveralls.io/github/CRAWLZSTAGE/infra?branch=benj)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/927edd47e2df4a9db9a941c40c0fc470)](https://www.codacy.com/app/jellyjellyrobot/infra?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CRAWLZSTAGE/infra&amp;utm_campaign=Badge_Grade)


[![Screenshot](images/output.gif)](https://crawlz.me)

## Was Ist Das?

CRAWLZ seeks to develop a database of Businesses worldwide. It allows a company to build a local cache of business contact information using only the search results from its user’s computing device.

## Architecture

This project is split into 5 containers, which can be scaled to fit processing tasks as defined by the user. We intend to atomize certain functions to introduce more scalablity and functionalities into the code base.

## Deployment

```
curl https://raw.githubusercontent.com/CRAWLZSTAGE/infra/master/docker-stack.yml > docker-stack.yml
docker stack deploy --compose-file=docker-stack.yml crawlz_stack
```

## Wiki

[Installation](INSTALL.md) instructions can be found here.

[Testing](TESTING.md) instructions can be found here.

[Current Deployment](DEPLOYMENT.md) information can be found here.