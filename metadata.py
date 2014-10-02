import os.path
import subprocess
import json
import re

class Create(object):
    def __init__(self, cuid, outfile, force):
        self.cuid = cuid
        self.force = force
        self.outfile = outfile

    @property
    def outfileexists(self):
        if os.path.isfile(self.outname):
            return True
        else:
            return False


    def assembledict(self, mydict, mykeys, dockjson):
        userdict = {'UserParams': {'restart': '', 'rm': '' , 'dockercommand': '',
                                 'sig-proxy':''
                                }}
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


    def checkcontaineruid(self, cuid):
        """Checks ID and returns valid containeruid. Accepts partial UID"""
        proc = subprocess.Popen(["docker ps -q"],
                                stdout=subprocess.PIPE, shell=True)
        out = proc.stdout.read()
        containeruids = out.split()
        if not len(cuid) >= 3:
            print "Container ID must be at least 3 characters"
            quit()
        else:
            # FIXME: match code failing on first
            #for containeruid in containeruids:
            #    print containeruid
            #    m = re.match(cuid, containeruid)
            #    if m:
            #        return containeruid
            #    else:
            #        print "Unable to find container ID '%s'. Try 'docker ps'." % cuid
            #        quit()
            if cuid in containeruids:
                return cuid
            else:
                print "Unable to find container ID '%s'. Try 'docker ps'." % cuid
                quit()

    def writeoutput(self, vals):
        if (not self.force) and (self.outfileexists):
            print ("{0} already exists. You can pass \
                   -f to override".format(self.outname))
            quit()
        with open(self.outname, "w") as outfile:
            json.dump(vals, outfile, indent=4)
        outfile.closed
        print ("Wrote {0}".format(self.outname))

    @property
    def outname(self):
        out = None
        if self.outfile:
            out = self.outfile
        else:
            out = "{0}.json".format(self.cuid)
        return out

    def metadata_file(self):
        cuid = self.checkcontaineruid(self.cuid)

        # Do I need to check if they are running?
        # docker inspect works on images and contianers
        # check if cuid is in the 'docker ps -a' list?

        mycommand = "docker inspect %s" % cuid
        containerproc = subprocess.Popen([mycommand],
                                         stdout=subprocess.PIPE, shell=True)
        dockjson = json.loads(containerproc.stdout.read())[0]

        newjson = dict
        newconfig = []
        newhost = dict

        configkeys = {'Config': {'AttachStderr', 'AttachStdin', 'AttachStdout',
                                 'CpuShares', 'Cpuset', 'Env', 'Hostname',
                                 'Image', 'Memory', 'Tty', 'User', 'WorkingDir'
                                 },
                      'HostConfig': {'Binds', 'CapAdd', 'CapDrop', 'ContainerIDFile', 'Dns',
                                     'DnsSearch', 'Links', 'LxcConf', 'NetworkMode',
                                     'PortBindings', 'Privileged', 'PublishAllPorts'
                                     }
                      }

        vals = self.assembledict(newconfig, configkeys, dockjson)
        self.writeoutput(vals)
