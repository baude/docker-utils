# Python wrapper for docker
# Imports json file and calls docker

import json
import os
import jsonschema
import subprocess

class Run(object):
    def __init__(self, command, jsonfile):
        self.dockercommand = command
        self.jsonfile = jsonfile
        # FIXME
        self.remove = True

    def load_json(self):
        # FIXME: needed?
        json_data = open(self.jsonfile).read()
        # FIXME: schema file missing
        #json_schema = open("docker-wrapper-schema.json").read()

        try:
            #jsonschema.validate(json.loads(json_data), json.loads(json_schema))
            json_data = open(self.jsonfile)
            return json.load(json_data)

        except:
            # FIXME
            print "no worky"
            return False
        #except jsonschema.ValidationError as e:
        #    raise e.message
        #except jsonschema.SchemaError as e:
        #    raise e


        # not used?
        #dockerrundict = {"Image":"image"}

    def mystringreplace(self, mystring, myarg):
        return mystring.replace(myarg,"")

    def formfinaldict(self, mydict):
        newdict = {}
        keymap = {'CpuShares':'cpu-shares', 'Cpuset':'cpuset', 'Env':'env', 'Hostname':'hostname',
                'Image':'image', 'Memory':'memory', 'Tty':'tty', 'User':'user', 'WorkingDir':'workdir',
                'CapAdd':'cap-add', 'CapDrop':'cap-drop', 'ContainerIDFile':'cidfile', 'Dns':'dns',
                'DnsSearch':'dns-search', 'Links':'link', 'LxcConf':'lxc-conf', 'NetworkMode':'net',
                'PortBindings':'publish', 'Privileged':'privileged', 'PublishAllPorts':'publish=all',
                'Binds':'volume'
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
            #hostip = mydict['PortBindings]'
            print ""
            pbind = []
            for k,v in mydict['PortBindings'].iteritems():
                containerport = self.mystringreplace(mystringreplace(k,"/tcp"),"/udp")
                if v[0]['HostIp'] == "":
                    #pbind.append(("{0}::{1}".format(mydict['PortBindings'][k][0]['HostPort'])))
                    hostport = mydict['PortBindings'][k][0]['HostPort']
                    pbind.append(("{0}:{1}".format(hostport, containerport)))
                else:
                    hostip= v[0]['HostIp']
                    hostport = mydict['PortBindings'][k][0]['HostPort']
                    pbind.append(("{0}:{1}:{2}".format(hostip, hostport, containerport)))
            newdict['publish'] = pbind
            del mydict['PortBindings']

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
                    containername=params[num][l2]
                    #params.pop(num)
                    break
                for k,v in params[num][l2].iteritems():
                    if v not in [0,"None",None,"",[]]:
                        newdict[k] =v
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

        dockerargs = self.dockerparamform(params)
        if self.remove == True:
            dockerargs = dockerargs + ("{0}".format("--rm "))
        dockerargs = dockerargs + ("--name={0}".format(containername))
        print "docker %s %s %s" % (self.dockercommand, dockerargs, image)
        print ""
        os.system("docker %s %s %s" % (self.dockercommand, dockerargs, image))


    def containernameexists(self, name):
        mycommand = "docker ps -a -q"
        proc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        out = proc.stdout.read()
        containeruids = out.split()
        insopen = "{{"
        insclose = "}}"
        for containers in containeruids:
            inspect = ("docker inspect --format='{0}.Name{1}' {2}".format(insopen,insclose,containers))
            proc = subprocess.Popen([inspect], stdout=subprocess.PIPE, shell=True)
            containname = proc.stdout.read().rstrip('\n')
            name = str(name)
            if (containname == name):
                return True
        return False


    def start_container(self):
        # Need to interpose dictionary values into usable commands
        params = self.load_json()
        print params
        image = params[0]['Config']['Image']
        del params[0]['Config']['Image']
        foobar, containername = self.stripParams(params)
        if (self.containernameexists(containername)):
            print ("\n{0} already exists as a container name and cannot be reused".format(containername))
            quit()
        else:
            barfoo = self.formfinaldict(foobar)
        self.dockerrun(barfoo, image, containername)

