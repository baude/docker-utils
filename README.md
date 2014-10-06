# docker-utils

Provides a way to specify how an image should be run. A set of utilities to simplify running and managing Docker containers. In the same way a Dockerfile provides a syntax for building images, docker-utils provides a way to specify how an image should be run.

* share images with defined `docker run` parameters
* manage running containers through a terminal dashboard

## installation
`pip install -r requirements.txt`

> NOTE: docker-dash.py requires python [urwid](http://excess.org/urwid/wiki/Installation)

## Utilities

### container-template.py
Generates docker run metadata (json) and runs containers based on that metadata.

Create run metadata:
```
./container-template.py create <docker_container_id> [--force][--oufile myapp.json]
Wrote myapp.json
```
Run an image based on metadata:
```
./container-template.py run myapp.json
docker run myapp
12b3fff309c3
```
List metadata files in `/var/container-templates/`. Include current working directory if `--local`:
```
./container-template.py list --local
foo.json
bar.json
myapp.json
82f000691b9a.json
dd4281fb5f25.json
```

Pull a metadata file from a remote source:
```
./container-template.py pull http://example.com/myapp.json
Wrote myapp.json
```
Default filename is remote filename. Use `--output mycoolapp.json` to override default.

Files are written to current working directory. Use `--install` to write file to system directory `/var/container-templates`.
```
./container-template.py pull http://example.com/myapp.json --install
Wrote /var/container-templates/myapp.json
```

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
