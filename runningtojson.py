#!/usr/bin/env python

import os
import os.path
import subprocess
import json
import re
import argparse

print " "


def outfileexists(outname):
    if os.path.isfile(outname):
        return True
    else:
        return False


def assembledict(mydict, mykeys, dockjson):
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


def checkcontaineruid(cuid):
    """Checks ID and returns valid containeruid. Accepts partial UID"""
    proc = subprocess.Popen(["docker ps -q"],
                            stdout=subprocess.PIPE, shell=True)
    out = proc.stdout.read()
    containeruids = out.split()
    if not len(cuid) >= 3:
        print "Container ID must be at least 3 characters"
        quit()
    else:
        for containeruid in containeruids:
            m = re.match(cuid, containeruid)
            if m:
                return containeruid
            else:
                print "Unable to find container ID '%s'. Try 'docker ps'." % cuid
                quit()


def writeoutput(outfile):
    exists = outfileexists(outname)
    if (not args.force) and (exists):
        print ("{0} already exists. You can pass \
               -f to override".format(outname))
        quit()
    with open(outname, "w") as outfile:
        json.dump(vals, outfile, indent=4)
    outfile.closed
    print ("Wrote {0}".format(outname))

parser = argparse.ArgumentParser()
parser.add_argument("cuid",
                    metavar="CONTAINER_ID",
                    help="Container ID. Provide at least 3 characters.")
parser.add_argument("-f", "--force", default=False,
                    action="store_true",
                    help="Force overwriting the output file")

args = parser.parse_args()

cuid = checkcontaineruid(args.cuid)

# Do I need to check if they are running?
# docker inspect works on images and contianers
# check if cuid is in the 'docker ps -a' list?

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
              'HostConfig': {'Binds', 'CapAdd', 'CapDrop', 'ContainerIDFile', 'Dns',
                             'DnsSearch', 'Links', 'LxcConf', 'NetworkMode',
                             'PortBindings', 'Privileged', 'PublishAllPorts'
                             }
              }

vals = assembledict(newconfig, configkeys, dockjson)
writeoutput(outname)
