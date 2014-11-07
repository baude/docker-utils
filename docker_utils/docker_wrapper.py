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

# Python wrapper for docker
# Imports json file and calls docker

import json
import os
import subprocess
import docker
import time
from docker_utils import metadata


class Run(object):
    def __init__(self, **kwargs):
        #self.dockercommand = kwargs['command']
        self.jsonfile = kwargs['jsonfile']
        # FIXME
        self.remove = True

    def load_json(self):
        # FIXME: needed?
        json_data = open(self.jsonfile).read()
        # FIXME: schema file missing
        # json_schema = open("docker-wrapper-schema.json").read()

        try:
            # jsonschema.validate(json.loads(json_data), json.loads(json_schema))
            json_data = open(self.jsonfile)
            return json.load(json_data)

        except:
            # FIXME
            print "no worky"
            return False
        # except jsonschema.ValidationError as e:
        #    raise e.message
        # except jsonschema.SchemaError as e:
        #    raise e
        # not used?
        # dockerrundict = {"Image":"image"}

    def mystringreplace(self, mystring, myarg):
        return mystring.replace(myarg, "")

    def formfinaldict(self, mydict):
        newdict = {}
        keymap = {'CpuShares': 'cpu-shares', 'Cpuset': 'cpuset', 'Env': 'env', 'Hostname': 'hostname',
                  'Image': 'image', 'Memory': 'memory', 'Tty': 'tty', 'User': 'user', 'WorkingDir': 'workdir',
                  'CapAdd': 'cap-add', 'CapDrop': 'cap-drop', 'ContainerIDFile': 'cidfile', 'Dns': 'dns',
                  'DnsSearch': 'dns-search', 'Links': 'link', 'LxcConf': 'lxc-conf', 'NetworkMode': 'net',
                  'PortBindings': 'publish', 'Privileged': 'privileged', 'PublishAllPorts': 'publish=all',
                  'Binds': 'volume'
                  }
        # Assemble attach
        attach = []
        if 'AttachStdin' in mydict:
            attach.append("stdin")
            del mydict['AttachStdin']
        if 'AttachStdout' in mydict:
            attach.append("stdout")
            del mydict['AttachStdout']
        if 'AttachStderr' in mydict:
            attach.append("stderr")
            del mydict['AttachStderr']

        if len(attach) > 0:
            newdict['attach'] = attach

        if mydict['Hostname'] == "localhost":
            del mydict['Hostname']

        # Deal with port bindings
        if 'PortBindings' in mydict:
            # hostip = mydict['PortBindings]'
            print ""
            pbind = []
            for k, v in mydict['PortBindings'].iteritems():
                containerport = self.mystringreplace(self.mystringreplace(k, "/tcp"), "/udp")
                if v[0]['HostIp'] == "":
                    # pbind.append(("{0}::{1}".format(mydict['PortBindings'][k][0]['HostPort'])))
                    hostport = mydict['PortBindings'][k][0]['HostPort']
                    pbind.append(("{0}:{1}".format(hostport, containerport)))
                else:
                    hostip = v[0]['HostIp']
                    hostport = mydict['PortBindings'][k][0]['HostPort']
                    pbind.append(("{0}:{1}:{2}".format(hostip, hostport, containerport)))
            newdict['publish'] = pbind
            del mydict['PortBindings']

        # Grab the docker CMD
        newdict['dockercommand'] = mydict['Cmd'][0]
        del mydict['Cmd']

        # Push left over values to newdict
        for keys in mydict.keys():
            if keys in keymap:
                newdict[keymap[keys]] = mydict[keys]

        return newdict

    def stripParams(self, params):
        newdict = {}
        containername = ""
        for num in range(len(params)):
            for l2 in params[num].iterkeys():
                if l2 == "Name":
                    containername = params[num][l2]
                    # params.pop(num)
                    break
                for k, v in params[num][l2].iteritems():
                    if v not in [0, "None", None, "", []]:
                        newdict[k] = v
        return newdict, containername

    def dockerparamform(self, params):
        dockerargs = ""
        for keys in params.keys():
            if type(params[keys]) == list:
                # Has a list, needs to be parsed
                for i in params[keys]:
                    dockerargs = dockerargs + "--%s=%s " % (keys, i)
            else:
                dockerargs = dockerargs + "--%s=%s " % (keys, params[keys])
        return dockerargs

    def dockerrun(self, params, image, containername):
        dockercmd = params['dockercommand']
        del params['dockercommand']
        dockerargs = self.dockerparamform(params)
        if self.remove == True:
            dockerargs = dockerargs + ("{0}".format("--rm "))
        dockerargs = dockerargs + ("--name={0}".format(containername))
        print "docker %s %s %s %s" % (self.dockercommand, dockerargs, image, dockercmd)
        print ""
        os.system("docker %s %s %s %s" % (self.dockercommand, dockerargs, image, dockercmd))

    def containernameexists(self, name):
        mycommand = "docker ps -a -q"
        proc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        out = proc.stdout.read()
        containeruids = out.split()
        insopen = "{{"
        insclose = "}}"
        for containers in containeruids:
            inspect = ("docker inspect --format='{0}.Name{1}' {2}".format(insopen, insclose, containers))
            proc = subprocess.Popen([inspect], stdout=subprocess.PIPE, shell=True)
            containname = proc.stdout.read().rstrip('\n')
            name = str(name)
            if (containname == name):
                return True
        return False

    def start_container(self):
        imagecommands = ImageFunctions()
        dcons = MakeDConnect()
        djs = DockerJSON()
        params = self.load_json()
        djs.parsejson(params)
        if not imagecommands.imageExistsByName(djs.image):
            print "Pulling image..."
            dcons.c.pull(djs.image)
        newcontainer = dcons.c.create_container(djs.image, None, djs.hostname, djs.user,
                       None, None, None, djs.mem_limit, djs.ports, djs.environment, djs.dns,
                       djs.volumes, djs.volumes_from, djs.network_disabled, djs.name,
                       djs.entrypoint, djs.cpu_shares, djs.working_dir, djs.domainname, djs.memswap_limit)
        print "Created new container {0}".format(newcontainer['Id'])
        dcons.c.start(newcontainer['Id'], None, djs.port_bindings, djs.lxc_conf, djs.publish_all_ports, djs.links, djs.priviledged, djs.dns, djs.dns_search, djs.volumes_from, djs.network_mode)
        kwargs = {'cuid': newcontainer['Id'][:8], 'outfile': None, 'directory': None, 'force': True}
        create = metadata.Create(**kwargs)
        create.write_files()




class DockerJSON(object):

    def parsejson(self, params):

        # Container Create

        """
        self, image, command=None, hostname=None, user=None,
                         detach=False, stdin_open=False, tty=False,
                         mem_limit=0, ports=None, environment=None, dns=None,
                         volumes=None, volumes_from=None,
                         network_disabled=False, name=None, entrypoint=None,
                         cpu_shares=None, working_dir=None, domainname=None,
                         memswap_limit=0):
        """

        self.image = params[0]['Image']
        self.hostname = params[0]['Config']['Hostname']
        self.user = params[0]['Config']['User']
        # detach
        # stdin
        # tty
        self.mem_limit = params[0]['Config']['MemorySwap']
        self.ports = params[0]['NetworkSettings']['Ports']
        self.environment = params[0]['Config']['Env']
        self.dns = params[0]['HostConfig']['Dns']
        self.volumes = params[0]['Config']['Volumes']
        self.volumes_from = params[0]['HostConfig']['VolumesFrom']
        self.network_disabled = params[0]['Config']['NetworkDisabled']
        self.name = params[0]['Name']
        self.entrypoint = params[0]['Config']['Entrypoint']
        self.cpu_shares = params[0]['Config']['CpuShares']
        self.working_dir = params[0]['Config']['WorkingDir']
        self.domainname = params[0]['Config']['Domainname']
        self.memswap_limit = params[0]['Config']['MemorySwap']

        # Container Start

        """
        container, binds=None, port_bindings=None, lxc_conf=None,
              publish_all_ports=False, links=None, privileged=False,
              dns=None, dns_search=None, volumes_from=None, network_mode=None
        """

        # binds

        self.port_bindings = params[0]['HostConfig']['PortBindings']
        self.lxc_conf = params[0]['HostConfig']['LxcConf']
        self.publish_all_ports = params[0]['HostConfig']['PublishAllPorts']
        self.links = params[0]['HostConfig']['Links']
        self.priviledged = params[0]['HostConfig']['Privileged']
        self.dns_search = params[0]['HostConfig']['DnsSearch']
        self.network_mode = params[0]['HostConfig']['NetworkMode']


class ImageFunctions(object):

    def imageExistsByName(self, iname):
        cons = MakeDConnect()
        images = cons.c.images(name=None, quiet=False, all=True, viz=False)
        for image in images:
            for repo in image['RepoTags']:
                if repo.startswith(iname):
                    return True
        return False


class MakeDConnect(object):
    def __init__(self):
        self.c = docker.Client(base_url='unix://var/run/docker.sock', version='1.12', timeout=10)
