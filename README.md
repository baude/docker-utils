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
A terminal dashboard to stop, delete and enter running containers. Accepts comma- or space-speparated lists for all commands.

```./docker-dash.py
$ sudo ./docker-dash.py

#  ID           Image           Status  
 0 064c5f85     rhel7           Running 
 1 2536412b     rhel7           Not Running
 2 dee33dcd     rhel7           Not Running
 3 c95d33db     rhel7           Not Running
 4 670fa3ff     rhel7           Not Running
 5 85c601b2     rhel7           Not Running
 6 f917cff6     centos          Not Running
 7 dfe49c18     pulp/pulp-admin Not Running
 
Command Reference: (q)uit (r)efresh (s)top (d)elete (p)eek
 
Command: p
 
Which Container(s)?: 0
bash-4.2# exit
 
#  ID           Image           Status  
 0 064c5f85     rhel7           Running 
 1 2536412b     rhel7           Not Running
 2 dee33dcd     rhel7           Not Running
 3 c95d33db     rhel7           Not Running
 4 670fa3ff     rhel7           Not Running
 5 85c601b2     rhel7           Not Running
 6 f917cff6     centos          Not Running
 7 dfe49c18     pulp/pulp-admin Not Running
 
Command Reference: (q)uit (r)efresh (s)top (d)elete (p)eek
 
Command: s
 
Which Container(s)?: 0
 
...
```
