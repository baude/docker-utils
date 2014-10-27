#!/usr/bin/env python

import os
import subprocess
import json
import time
import argparse
import threading
import string
import docker

dellist = []

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--all", help="Work with non-active containers too", action="store_true")
parser.add_argument("-i", "--images", help="Jump into the images interface", action="store_true")

args = parser.parse_args()

allcontains = False
if args.images:
    myscreen = "images"
else:
    myscreen = "containers"


if args.all:
    print "View all containers"
    allcontains = True

def getcontainerinfo(containeruids):
    """ This function takes an array of of container uids and
    returns an array of dicts with the inspect info
    """
    cdetails = list()
    for containers in containeruids:
        #mycommand = "docker inspect %s" % containers
        #containerproc = subprocess.Popen([mycommand], stdout=subprocess.PIPE, shell=True)
        #cdetails.append(json.loads(containerproc.stdout.read())[0])
        cdetails.append(c.inspect_container(containers['Id']))
    return cdetails


def getcontainersummary(containerinfo):
    """
    This function takes a container and returns its run state
    """

    cuid = containerinfo['Id']
    cimage = containerinfo['Image']
    if 'Up' in containerinfo['Status']:
        crun = "Running"
    else:
        crun = "Not Running"
    return cuid[:8],  cimage, crun


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
        

def getpid(cid):
    #return containarray[int(mynum)]['State']['Pid']
    cinspect = c.inspect_container(cid)
    return cinspect['State']['Pid']


def isRunning(containarray, mynum):
    #print containarray
    #if (containarray[int(mynum)]['State']['Running']):
    if 'Up' in  (containarray[int(mynum)]['Status']):
        return True
    else:
        return False

def returnuid(containarray, mynum):
    myuid = containarray[int(mynum)]['Id']
    return myuid[:8]

def returnfulluid(iid):
    i = c.images(name=None, quiet=False, all=True, viz=False)
    for f in i:
        if f['Id'].startswith(iid):
            return f['Id']


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
    global myscreen
    stopcontainers = raw_input("Which {0}(s)?: ".format(myscreen))
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


def stopcontainers(cid, cpid):
    print "Stopping {0}".format(cid)
    #stopprocess = subprocess.call([myval], stdout=subprocess.PIPE, shell=True)
    stopprocess =  c.stop(cid, None)

    lambda: os.waitpid(cpid,0)

def startcontainers(cid):
    c.start(cid)


def convertsize(kbytes):
    if kbytes > 1000000000:
        ksize = str(round(float(kbytes / 1000000000),2)) + " GB"
    else:
        
        ksize = str((int(kbytes / 1000000))) + " MB"

    return ksize


def findchild(imageid, images):
    imagenode = []
    for i in images:
        if i['ParentId'] == imageid:
            imagenode.append(i['Id'])
    if len(imagenode) == 0:
        # No more children
        return False
    elif len(imagenode) == 1:
        return imagenode
    else:
        return imagenode

def crawl(nodeid, images):
    global dellist
    imagechild = ""
    imagechild = findchild(nodeid, images)
    if imagechild is not False:
        dellist.append(imagechild)
        if type(imagechild) == list:
               for i in imagechild:
                   if crawl(i, images) is False:
                      break 
    return dellist

def deleteimage(iid):
    if type(iid) == list:
        for i in iid:
            deleteimage(i)
    else:
        print "Deleting {0}".format(iid)
        c.remove_image(iid, noprune=True)
        ##c.remove_image(iid)

def deletecontainer(c, cid):
    try:
        print "Deleting %s" % cid
        c.remove_container(cid, v=False, link=False)
    except:
        print "Unable to find that container ..."


def checkforcontainers(imagelist, c):
    delcontainers = []
    mycontainers = c.containers(quiet=False, all=True, trunc=True, latest=False, since=None, before=None, limit=-1)
    # Get all of the image inspect information
    inspectinfo = []
    for j in mycontainers:
        myinspect = c.inspect_container(j['Id'])
        inspectinfo.append(myinspect)

    for i in imagelist:
        if type(i) == list:
            for s in i:
                myid = s
        else:
            myid = i
        for c in inspectinfo:
            # print "{0} {1}".format(myid, c)
            if c['Image'] == myid:
                state = "Off"
                if c['State']['Running'] == True:
                    state="Running"

                mydict = {'Id': c['Id'][:25], 'Image': c['Config']['Image'], 'Name': c['Name'], 'State': state, 'Pid': c['State']['Pid']}
                delcontainers.append(mydict)

    return delcontainers 


def printimagesummary():
    global myscreen
    global allcontains
    myscreen = "images"
    dockall = showall(allcontains)
    images = c.images(name=None, quiet=False, all=allcontains, viz=False)
    # Map is: Created, VirtualSize, RepoTags[], Id 
    print 
    if len(images) > 1:
        print ('{0:2} {1:20} {2:10} {3:18} {4:8}'.format(" #", "Repo",  "Image ID ","Created", "Size"))
        for s in range(len(images)):
            imagedesc = images[s]['RepoTags'][0].split(':')[0]
            if len(images[s]['RepoTags']) > 1:
                imagedesc = imagedesc + ":" + images[s]['RepoTags'][0].split(':')[1]
            created = time.strftime("%d %b %y %H:%M",time.localtime(images[s]['Created']))
            isize = convertsize(float(images[s]['VirtualSize']))
            print ('{0:2} {1:20} {2:10} {3:18} {4:8}'.format(s, imagedesc, images[s]['Id'][:8], created, isize))
    else:
        print "No images ..."
    print " "
    print "GUI Reference: (c) containers (q)uit (re)fresh"
    print "Image Reference: (r)un (d)elete (p)eek"
    print " "
    containernum = raw_input("Command: ")
    if containernum.upper() == "A":
        if allcontains == True:
            allcontains = False
        else:
            allcontains = True
        printimagesummary()
    if containernum.upper() == "RE":
        printimagesummary()
    if containernum.upper() == "C":
        printsummary2()
    if containernum.upper() == "Q":
        quit()
    if containernum.upper() == "D":
        global dellist
        delimages = getcontainer(images)
        allimages = c.images(name=None, quiet=False, all=True, viz=False)
        for d in delimages:
            imagelist = []
            iid = images[int(d)]['Id']
            dellist.append(iid)
            imagelist = crawl(iid, allimages)
            delcontainers = checkforcontainers(imagelist, c)
            if delcontainers > 0:
                print "The following containers would also be stopped and deleted."
                print " "
                for cons in delcontainers:
                    print "{0:12} {1:15} {2:15} {3:10}".format(cons['Id'], cons['Image'], cons['Name'], cons['State'])
                print " "
                confirm = raw_input("Continue?  (y/n) : ")
                if confirm.upper() == "Y":
                    for dels in delcontainers:
                        if dels['State'] == "Running":
                            stopcontainers(dels['Id'], dels['Pid'])
                        deletecontainer(c, dels['Id'])
                else:
                    print "Not deleting ..."
                    time.sleep(2)
                    printimagesummary()

            for i in reversed(imagelist):
                deleteimage(i)
            del imagelist[:]
        printimagesummary()


def getimagesummary(iuid):
    """
    This function takes a container and returns its run state
    """
    
    cuid = containerinfo['Id']
    cimage = containerinfo['Config']['Image']
    return cuid[:8], cimage, crun

def printsummary2():
    print "hello"
    global allcontains
    print allcontains
    #dockall = showall(allcontains)
    mycontainers = c.containers(quiet=False, all=allcontains, trunc=True, latest=False, since=None, before=None, limit=-1)
    if len(mycontainers) != 0:
        print ('{0:2} {1:12} {2:25} {3:8}'.format(" #", "ID","Image","Status"))
        for s in range(len(mycontainers)):
            chostname, cimage, crun = getcontainersummary(mycontainers[s])
            print ('{0:2} {1:12} {2:25} {3:8}'.format(s, chostname, cimage, crun))
    else:
        print "No active containers ..."
    print " "
    print "GUI Reference: (q)uit (i)mages (re)fresh show (a)ll"
    print "Container Reference: (r)un (s)top (d)elete (p)eek"
    print " "
    containernum = raw_input("Command: ")
    if containernum.upper() == "A":
        if allcontains == True:
            allcontains = False
        else:
            allcontains = True
        printsummary2()
    if containernum.upper() == "I":
        printimagesummary()
    if containernum.upper() == "x":
        printsummary2()
    if containernum.upper() == "Q":
        quit()
    if containernum.upper() == "S":
        stopcontainer = getcontainer(mycontainers)
        stopthreads = []
        for container in stopcontainer:
            cid = returnuid(mycontainers, container)
            if not isRunning(mycontainers, container):
                print "%s is not running" % cid
                time.sleep(1)
                break
            cpid = getpid(cid)
            #print "-----------------"
            #print cpid
            #print "-----------------"
            t = threading.Thread(target=stopcontainers, args=(cid, cpid,))
            
            stopthreads.append(t)
            t.start()
        print "Waiting for containers to stop"
        [x.join() for x in stopthreads]
        printsummary2()

    if containernum.upper() == "R":
        startthreads = []
        runcontainer = getcontainer(mycontainers)
        for container in runcontainer:
            cid = returnuid(mycontainers, container)
            cdetails = getcontainerinfo(mycontainers)
            if isRunning(mycontainers, container):
                print "%s is already running" % cid
                time.sleep(1)
                break
            myval = ("docker start {0}".format(cid))
            t = threading.Thread(target=startcontainers, args=(cid,))
            startthreads.append(t)
            t.start()
        print "Waiting for containers to start"
        [x.join() for x in startthreads]
        printsummary2()

    if containernum.upper() == "D":
       cdetails = getcontainerinfo(mycontainers)
       delcontainer = getcontainer(cdetails)
       for container in delcontainer:
            cid = returnuid(mycontainers, container)
            deletecontainer(c,cid)
          # try:
          #     print "Deleting %s" % cid
          #     c.remove_container(cid, v=False, link=False)
          # except:
          #     print "Unable to find that container ..."
       printsummary2()

    if containernum.upper() == "P":
        cdetails = getcontainerinfo(mycontainers)
        peekcontainer = getcontainer(cdetails)
        if peekcontainer != False:
            for container in peekcontainer:
                if not isRunning(mycontainers, container):
                    print " "
                    print ("{0} is not a running container".format(returnuid(cdetails, container)))
                    time.sleep(2)
                    printsummary2()
                cid = returnuid(mycontainers, container)
                cpid = getpid(cid)
                print "Entering container %s" % returnuid(cdetails, container)
                foo = terminal2(cpid)
        printsummary2()
    else:
        printsummary2() 


if __name__ == '__main__':
    c = docker.Client(base_url='unix://var/run/docker.sock',
                  version='1.12',
                  timeout=10)
    #myscreen="containers"

    if myscreen == "containers":
        printsummary2()
    elif myscreen == "images":
        printimagesummary()
