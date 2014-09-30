#!/usr/bin/env python

import os
import subprocess
import json
import urwid
import re
import time

def getcontainerinfo(containeruids):
    cdetails = list ()
    for containers in containeruids:
        mycommand = "docker inspect %s" % containers
        containerproc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        cdetails.append(json.loads(containerproc.stdout.read())[0])
    return cdetails

def getsummary(containerinfo):
    #chostname = containerinfo['Config']['Hostname']
    cuid = containerinfo['Id']
    #ccmd = containerinfo['HostConfig']['Cmd']
    cimage = containerinfo['Config']['Image']
    if containerinfo['State']['Running'] == 1:
        crun = "Running"
    else:
        crun = "Not Running"
    return cuid[:8], cimage, crun


def isInt(mystr):
    try:
        int(mystr)
        return True
    except ValueError:
        return False

def in2list(inlist):
    """Converts input string into valid list

    Parses spaces and/or commas"""
    delim = None
    if re.search(",", inlist):
        delim = ","
    else:
        delim = " "
    inlist = delim.join(inlist.split(delim))
    return inlist.split(delim)

def terminal(cpid):
    #myval = ["sudo","nsenter","-m","-u","-n","-i","-p","-t", cpid]
    #myval = ["ls], [\-l"]
    myval = ["ls && sleep(5)"]
    #term = urwid.Terminal(myval)
    term = urwid.Terminal(None)

    #myval = ("sudo nsenter -m -u -n -i -p -t {0} /bin/bash".format(cpid))
    mainframe = urwid.LineBox(
        urwid.Pile([
            ('weight', 70, term),
            ('fixed', 1, urwid.Filler(urwid.Edit('focus test edit: '))),
        ]),
    )

    def set_title(widget, title):
        mainframe.set_title(title)

    def quit(*args, **kwargs):
        raise urwid.ExitMainLoop()

    def handle_key(key):
        if key in ('q', 'Q'):
            quit()

    urwid.connect_signal(term, 'title', set_title)
    urwid.connect_signal(term, 'closed', quit)

    loop = urwid.MainLoop(
        mainframe,
        handle_mouse=False,
        unhandled_input=handle_key)

    term.main_loop = loop
    term.command = myval
    loop.run()

def terminal2(cpid):
    nsenter = ('sudo nsenter -m -u -n -i -p -t {0} /bin/bash'.format(cpid))
    import pty
    pty.spawn(nsenter.split())

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
    stopcontainers = in2list(stopcontainers)
    if containerinrange(cdetails, stopcontainers) == False:
        return False
    for container in stopcontainers:
        # FIXME: check if it's valid integer
        if not(isInt(container)):
            print " "
            print ("{0} isn't a integer...".format(container))
            time.sleep(2)
            return False
        else:
            return stopcontainers


def printsummary():
    print " "
    proc = subprocess.Popen(["docker ps -qa"], stdout=subprocess.PIPE, shell=True)
    out = proc.stdout.read()
    containeruids = out.split()
    cdetails = getcontainerinfo(containeruids)
    print ('{0:2} {1:12} {2:15} {3:8}'.format("#", "ID","Image","Status"))
    for s in range(len(cdetails)):
        chostname, cimage, crun = getsummary(cdetails[s])
        print ('{0:2} {1:12} {2:15} {3:8}'.format(s, chostname, cimage, crun))

    print " "
    print "Command Reference: (q)uit (r)efresh (s)top (d)elete (p)eek"
    print " "
    containernum = raw_input("Command: ")
    if containernum.upper() == "R":
        printsummary()
    if containernum.upper() == "Q":
        quit()
    if containernum.upper() == "S":
        stopcontainer = getcontainer(cdetails)
        for container in stopcontainer:
            try:
                cid = returnuid(cdetails, container)
                print "Stopping %s" % cid
                myval = ("docker stop {0}".format(cid))
                stopprocess = subprocess.Popen([myval], stdout=subprocess.PIPE, shell=True)

            except:
                print "Unable to find that container..."
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

if __name__ == '__main__':
    printsummary()
