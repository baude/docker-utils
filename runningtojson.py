import os
import os.path
import subprocess
import json
from optparse import OptionParser

print " "


def outfileexists(outname):
    if os.path.isfile(outname):
        return True
    else:
        return False


def assembledict(mydict, mykeys, dockjson):
    for desc in mykeys:
        newdict = {desc: {}}
        for keys in mykeys[desc]:
            newdict[desc][keys] = dockjson[desc][keys]
        mydict.append(newdict)
    return mydict


def checkcontaineruid(cuid):
    proc = subprocess.Popen(["docker ps -q"],
                            stdout=subprocess.PIPE, shell=True)
    out = proc.stdout.read()
    containeruids = out.split()
    if cuid in containeruids:
        return True
    else:
        print "Unable to find the container ID"
        quit()


def writeoutput(myoptions, outfile):
    exists = outfileexists(outname)
    if (not myoptions.force) and (exists):
        print ("{0} already exists. You can pass \
               -f to override".format(outname))
        quit()
    with open(outname, "w") as outfile:
        json.dump(vals, outfile, indent=4)
    outfile.closed
    print ("Wrote {0}".format(outname))

usage = "usage: %prog containerid"
parser = OptionParser(usage)
parser.add_option("-f", "--force", dest="force", default=False,
                  action="store_true",
                  help="Force overwriting the output file")

(options, args) = parser.parse_args()
if len(args) == 0:
    parser.error("You must provide a container ID to convert")
    quit()

if len(args) > 1:
    parser.error("Too many inputs provided")

cuid = args[0]

# Do I need to account for portions of
# the cuid being used?

checkcontaineruid(cuid)

# Do I need to check if they are running?

outname = ("{0}.json".format(cuid))

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
              'HostConfig': {'CapAdd', 'CapDrop', 'ContainerIDFile', 'Dns',
                             'DnsSearch', 'Links', 'LxcConf', 'NetworkMode',
                             'PortBindings', 'Privileged', 'PublishAllPorts'
                             }
              }

vals = assembledict(newconfig, configkeys, dockjson)
writeoutput(options, outname)
