#!/usr/bin/env python

import os
import subprocess
import json
import time
import argparse
import threading
import string

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--all", help="Work with non-active containers too", action="store_true")
args = parser.parse_args()

allcontains = False

if args.all:
    print "View all containers"


def getcontainerinfo(containeruids):
    """ This function takes an array of of container uids and
    returns an array of dicts with the inspect info
    """
    cdetails = list()
    for containers in containeruids:
        mycommand = "docker inspect %s" % containers
        containerproc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        cdetails.append(json.loads(containerproc.stdout.read())[0])
    return cdetails


def getsummary(containerinfo):
    """
    This function takes a container and returns its run state
    """

    cuid = containerinfo['Id']
    cimage = containerinfo['Config']['Image']
    if containerinfo['State']['Running'] == 1:
        crun = "Running"
    else:
        crun = "Not Running"
    return cuid[:8], cimage, crun


def getimage(containerinfo):
    return string.replace(containerinfo[0]['Config']['Image'], "/", "")


def isInt(mystr):
    try:
        int(mystr)
        return True
    except ValueError:
        return False


def str2list(inlist):
    """Converts input string into valid list

    Parses spaces, commas and range of values('-')"""
    delim = " "
    if ',' in inlist:
        delim = ","
    inlist = delim.join(inlist.split(delim))
    containerlist = inlist.split(delim)
    rangelist = [containerlist.pop(r[0]) for r in enumerate(containerlist) if '-' in containerlist[r[0]]]
    for rl in rangelist:
        start, end = rl.split('-')
        containerlist.extend(range(int(start), int(end)+1))
    return containerlist


def terminal2(cpid):
    """
    This function takes a pid of a running container and opens it in 
    xterm if its available
    """
    nsenter = ('sudo nsenter -m -u -n -i -p -t {0} /bin/bash'.format(cpid))
    import pty
    import os
    if os.getenv('DISPLAY',"") == "":
        pty.spawn(nsenter.split())
    else:
        mycommand = "xterm -T {0} -e {1}".format(cpid, nsenter)
        containerproc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        

def getpid(containarray, mynum):
    return containarray[int(mynum)]['State']['Pid']

def isRunning(containarray, mynum):
    if (containarray[int(mynum)]['State']['Running']):
        return True
    else:
        return False

def returnuid(containarray, mynum):
    myuid = containarray[int(mynum)]['Id']
    return myuid[:8]

def containerinrange(cdetails, stopcontainers):
    for i in stopcontainers:
        foo = int(len(cdetails))
        foo = foo -1
        if not(isInt(i)):
            print " "
            print ("{0} isn't a integer...".format(i))
            time.sleep(2)
            return False
        if (0 <= int(i) <= foo) == False:
            print " "
            print ("{0} isn't a valid container number...".format(i))
            time.sleep(2)
            return False
    return True

def getcontainer(cdetails):
    """returns valid list of container IDs"""
    print " "
    stopcontainers = raw_input("Which Container(s)?: ")
    stopcontainers = str2list(stopcontainers)
    if containerinrange(cdetails, stopcontainers) == False:
        return False
    return stopcontainers

def showall(allcontains):
    if args.all:
        dockall = "-qa"
    elif allcontains == True:
        dockall = "-qa"
    else:
        dockall = "-q"
    return dockall

def printsummary():
    global allcontains
    print " "
    dockercmd = ["docker", "ps"]
    dockall = showall(allcontains)
    dockercmd.append(dockall)
    proc = subprocess.Popen(dockercmd, stdout=subprocess.PIPE )
    out = proc.stdout.read()
    containeruids = out.split()
    cdetails = getcontainerinfo(containeruids)
    if len(cdetails) != 0:
        print ('{0:2} {1:12} {2:25} {3:8}'.format(" #", "ID","Image","Status"))
        for s in range(len(cdetails)):
            chostname, cimage, crun = getsummary(cdetails[s])
            print ('{0:2} {1:12} {2:25} {3:8}'.format(s, chostname, cimage, crun))
    else:
        print "No active containers ..."
    print " "
    print "GUI Reference: (q)uit (re)fresh show (a)ll"
    print "Container Reference: (r)un (s)top (d)elete (p)eek"
    print " "
    containernum = raw_input("Command: ")
    if containernum.upper() == "A":
        if allcontains == True:
            allcontains = False
        else:
            allcontains = True
    if containernum.upper() == "x":
        printsummary()
    if containernum.upper() == "Q":
        quit()
    if containernum.upper() == "S":
        stopcontainer = getcontainer(cdetails)
        stopthreads = []
        for container in stopcontainer:
            cid = returnuid(cdetails, container)
            if not isRunning(cdetails, container):
                print "%s is not running" % cid
                time.sleep(1)
                break
            cpid = getpid(cdetails, container)
            myval = ("docker stop {0}".format(cid))
            t = threading.Thread(target=stopcontainers, args=(myval, cpid,))
            stopthreads.append(t)
            t.start()
        print "Waiting for containers to stop"
        [x.join() for x in stopthreads]
        printsummary()

    if containernum.upper() == "R":
        startthreads = []
        runcontainer = getcontainer(cdetails)
        for container in runcontainer:
            cid = returnuid(cdetails, container)
            cdetails = getcontainerinfo(containeruids)
            if isRunning(cdetails, container):
                print "%s is already running" % cid
                time.sleep(1)
                break
            myval = ("docker start {0}".format(cid))
            t = threading.Thread(target=startcontainers, args=(myval,))
            startthreads.append(t)
            t.start()
        print "Waiting for containers to start"
        [x.join() for x in startthreads]
        printsummary()


    if containernum.upper() == "D":
       delcontainer = getcontainer(cdetails)
       for container in delcontainer:
           try:
               cid = returnuid(cdetails, container)
               print "Deleting %s" % cid
               myval = ("docker rm {0}".format(cid))
               delprocess = subprocess.Popen([myval], stdout=subprocess.PIPE, shell=True)
           except:
               print "Unable to find that container ..."
       printsummary()

    if containernum.upper() == "P":
        peekcontainer = getcontainer(cdetails)
        if peekcontainer != False:
            for container in peekcontainer:
                if not isRunning(cdetails, container):
                    print " "
                    print ("{0} is not a running container".format(returnuid(cdetails, container)))
                    time.sleep(2)
                    printsummary()
                cpid = getpid(cdetails, container)
                print "Entering container %s" % returnuid(cdetails, container)
                foo = terminal2(cpid)
        printsummary()
    else:
        printsummary()

def stopcontainers(myval, cpid):
    stopprocess = subprocess.call([myval], stdout=subprocess.PIPE, shell=True)
    lambda: os.waitpid(cpid,0)

def startcontainers(myval):
    subprocess.call([myval], stdout=subprocess.PIPE, shell=True )

if __name__ == '__main__':
    printsummary()
