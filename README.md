# CRAWLZ

[![MIT License](https://img.shields.io/npm/l/stack-overflow-copy-paste.svg?style=flat-square)](http://opensource.org/licenses/MIT)
[![Build Status](https://travis-ci.org/CRAWLZSTAGE/infra.svg?branch=master)](https://travis-ci.org/CRAWLZSTAGE/infra)
[![Test Coverage](https://codeclimate.com/github/CRAWLZSTAGE/infra/badges/coverage.svg)](https://codeclimate.com/github/CRAWLZSTAGE/infra/coverage)
[![Code Climate](https://codeclimate.com/github/CRAWLZSTAGE/infra/badges/gpa.svg)](https://codeclimate.com/github/CRAWLZSTAGE/infra)
[![Coverage Status](https://coveralls.io/repos/github/CRAWLZSTAGE/infra/badge.svg?branch=benj)](https://coveralls.io/github/CRAWLZSTAGE/infra?branch=benj)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/927edd47e2df4a9db9a941c40c0fc470)](https://www.codacy.com/app/jellyjellyrobot/infra?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CRAWLZSTAGE/infra&amp;utm_campaign=Badge_Grade)


## Was Ist Das?

CRAWLZ seeks to develop a database of Businesses worldwide. It allows a company to build a local cache of business contact information using only the search results from its user’s computing device.

## Architecture

This project is split into 5 containers, which can be scaled to fit processing tasks as defined by the user. We intend to atomize certain functions to introduce more scalablity and functionalities into the code base. For example: 
- Captcha circumvention using machine learning or crowdsourcing

## Deployment

Currently, the code is/will be (TODO) be tested on
- a local environment with 4 cores
- 1 * DigitalOcean instance quad core instance
We intend to scale this up to span multiple computers in the future.

## Wiki

[Installation](INSTALL.md) instructions can be found here.

[Testing](TESTING.md) instructions can be found here.

[Current Deployment](DEPLOYMENT.md) information can be found here.