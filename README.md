# docker-utils

Provides a way to specify how an image should be run. A set of utilities to simplify running and managing Docker containers. In the same way a Dockerfile provides a syntax for building images, docker-utils provides a way to specify how an image should be run.

* share images with defined `docker run` parameters
* manage running containers through a terminal dashboard

## installation
`pip install -r requirements.txt`

> NOTE: docker-dash.py requires python [urwid](http://excess.org/urwid/wiki/Installation)

## Utilities

###runningtojson.py
Creates a json file describing the running container.

`./runningtojson.py <docker_container_id>`

### docker-wrapper.py
Takes the json file from runningtojson.py and runs a container with the specified `docker run` parameters.

`./docker-wrapper.py <output_from_runningtojson.json>`

### docker-dash.py
A terminal dashboard to start, stop and enter running containers

`./docker-dash.py`
