# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.4.0]

* Turn off cert verification for https healthchecks.  See comments in the code.

## [1.3.0]

* Fix issue with returning container ports as dict keys when list was expected
* Add in functionality to notify Docker containers for policy changes

## [1.2.0]

* Add the ability to force reauthentication for Docker login
* Handle connection errors for Docker login
