# Copyright (C) 2014 Brent Baude <bbaude@redhat.com>, Aaron Weitekamp <aweiteka@redhat.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import os
import subprocess
import json
import re
from string import Template

USER_TEMPLATE_DIR = "/var/container-template/user/"
SYSTEM_TEMPLATE_DIR = "/var/container-template/system/"

class Create(object):
    def __init__(self, **kwargs):
        self.cuid = kwargs['cuid']
        self.force = kwargs['force']
        self.outfile = kwargs['outfile']
        self.directory = kwargs['directory']

    def outfileexists(self, outname):
        if os.path.isfile(outname):
            return True
        else:
            return False


    def assembledict(self, mykeys, dockjson):
        # not used
        # instead of re-building the json, we take the whole thing
        userdict = {'UserParams': {'restart': '', 'rm': '' , 'dockercommand': '',
                                 'sig-proxy':''
                                }}
        mydict = []
        for desc in mykeys:
            newdict = {desc: {}}
            for keys in mykeys[desc]:
                newdict[desc][keys] = dockjson[desc][keys]
            mydict.append(newdict)
        if dockjson['Name'] != "":
            namedict = {'Name': dockjson['Name'] }
            mydict.append(namedict)
        mydict.append(userdict)
        return mydict


    def checkcontaineruid(self):
        """Checks ID and returns valid containeruid. Accepts partial UID"""
        proc = subprocess.Popen(["docker ps -q"],
                                stdout=subprocess.PIPE, shell=True)
        out = proc.stdout.read()
        containeruids = out.split()
        if not len(self.cuid) >= 3:
            print "Container ID must be at least 3 characters"
            quit(1)
        else:
            match = [containeruid for containeruid in containeruids if re.match(self.cuid, containeruid)]
            if match:
                 return match[0]
            else:
                print "Unable to find container ID '%s'. Try 'docker ps'." % self.cuid
                quit(1)

    def writeoutput(self, vals, outname, filetype="json"):
        if not self.directory:
            outname = USER_TEMPLATE_DIR + outname
        else:
            outname = self.directory + outname
        if (not self.force) and (self.outfileexists(outname)):
            print ("{0} already exists. Pass -f or --force to override".format(outname))
            quit(1)
        with open(outname, "w") as outfile:
            if filetype is "json":
                json.dump(vals, outfile, indent=4)
            else:
                outfile.write(vals)
        outfile.closed
        print outname

    @property
    def outname(self):
        out = None
        if self.outfile:
            out = self.outfile
        else:
            out = "{0}.json".format(self.cuid)
        return out

    @property
    def container_json(self):
        self.cuid = self.checkcontaineruid()

        # Do I need to check if they are running?
        # docker inspect works on images and contianers
        # check if cuid is in the 'docker ps -a' list?

        mycommand = "docker inspect %s" % self.cuid
        containerproc = subprocess.Popen([mycommand],
                                         stdout=subprocess.PIPE, shell=True)
        return json.loads(containerproc.stdout.read())[0]

    def metadata_file(self):
        # FIXME: populate these values
        userdict = {'UserParams': {'restart': '', 'rm': '' , 'dockercommand': '',
                                 'sig-proxy':''
                                }}

        # instead of re-building the json, we take the whole thing
        # TODO: filter out the irrelevant keys
        #configkeys = {'Config': {'AttachStderr', 'AttachStdin', 'AttachStdout',
        #                         'Cmd', 'CpuShares', 'Cpuset', 'Env', 'Hostname',
        #                         'Image', 'Memory', 'Tty', 'User', 'WorkingDir'
        #                         },
        #              'HostConfig': {'Binds', 'CapAdd', 'CapDrop', 'ContainerIDFile', 'Dns',
        #                             'DnsSearch', 'Links', 'LxcConf', 'NetworkMode',
        #                             'PortBindings', 'Privileged', 'PublishAllPorts'
        #                             }
        #              }

        vals = [self.container_json, userdict]
        self.writeoutput(vals, self.outname)

    def kubernetes_file(self):
        kube_file = self.outname.replace('.json', '-pod.json')
        schema = self.kube_schema
        # FIXME: need a better way to iterate over
        schema.update({'labels': {'name': self.container_json['Name']}})
        self.writeoutput(schema, kube_file)

    @property
    def kube_schema(self):
        return {
            "kind": "Pod",
            "id": None,
            "apiVersion": "v1beta1",
            "namespace": None,
            "creationTimestamp": None,
            "selfLink": None,
            "desiredState": {
                "manifest": {
                    "version": "v1beta1",
                    "id": None,
                    "containers": [{
                        "name": None,
                        "image": None,
                        "ports": [{
                            "containerPort": 6379,
                            "hostPort": 6379
                        }]
                    }]
                }
            },
            "labels": {
                "name": None
            }
        }

    @property
    def sysd_unit_template(self):
        return """[Unit]
Description=$name
After=docker.service
Requires=docker.service

[Service]
TimeoutStartSec=0
ExecStartPre=-/usr/bin/docker kill $name
ExecStartPre=-/usr/bin/docker rm $name
ExecStartPre=/usr/bin/docker pull $name
ExecStart=/usr/bin/docker run --name  $name $cmd

[Install]
WantedBy=multi-user.target
"""

    def sysd_unit_file(self):
        confcmd = "" if self.container_json['Config']['Cmd'] == None else self.container_json['Config']['Cmd']
        cmd = ' '.join(confcmd)
        repl_dict = {'name': self.container_json['Name'],
            'cmd': cmd}
        template = Template(self.sysd_unit_template)
        template = template.substitute(repl_dict)
        unit_filename = self.outname.replace('.json', '.service')
        self.writeoutput(template, unit_filename, "text")

    def write_files(self):
        self.metadata_file()
        self.kubernetes_file()
        self.sysd_unit_file()

class List(object):
    def __init__(self):
        self.pattern = 'service|json$'

    def metadata_files(self):
        dirlist = [USER_TEMPLATE_DIR, SYSTEM_TEMPLATE_DIR]
        files = [d + f for d in dirlist for f in os.listdir(d) if re.search(self.pattern, f)]
        for f in files:
            print f

class Pull(object):
    def __init__(self, **kwargs):
        self.force = kwargs['force']
        self.directory = kwargs['directory']
        self.outfile = kwargs['outfile']
        self.response = None

    def get_url_filename(self):
        import cgi
        _, params = cgi.parse_header(self.response.headers.get('Content-Disposition', ''))
        return params['filename']

    @property
    def outname(self):
        filename = None
        if self.outfile:
            filename = self.outfile
        else:
            filename = self.get_url_filename()
        if not self.directory:
            return "{0}/{1}".format(USER_TEMPLATE_DIR, filename)
        else:
            return "{0}/{1}".format(self.directory, filename)

    def pull_url(self, url):
        from urllib2 import Request, urlopen, URLError
        req = Request(url)
        try:
            response = urlopen(req)
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
        else:
            self.response = response
            self.writeoutput()

    @property
    def outfileexists(self):
        return os.path.isfile(self.outname)

    def writeoutput(self):
        if (not self.force) and (self.outfileexists):
            print ("{0} already exists. Pass -f or --force to override".format(self.outname))
            quit(1)
        else:
            with open(self.outname, "w") as outfile:
                outfile.write(self.response.read())
            outfile.closed
            print self.outname
