import os
import subprocess
import json
import urwid

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
    os.system(('sudo nsenter -m -u -n -i -p -t {0} /bin/bash'.format(cpid)))
    
def getpid(containarray, mynum):
    return containarray[int(mynum)]['State']['Pid']

def returnuid(containarray, mynum):
    myuid = containarray[int(mynum)]['Id']
    return myuid[:8]

def getcontainer():
    print " "
    stopcontainer = raw_input("Which Container?: ")
    if (isInt(stopcontainer)):
        return stopcontainer
    else:
        print " "
        print ("{0} isn't a integer...".format(stopcontainer))
    

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
        stopcontainer = getcontainer()
        try:
            cid = returnuid(cdetails, stopcontainer)
            myval = ("docker stop {0}".format(cid))
            stopprocess = subprocess.Popen([myval], stdout=subprocess.PIPE, shell=True)
            printsummary()

        except:
            print "Unable to find 3  that container..."
        
    if containernum.upper() == "D":
       delcontainer = getcontainer() 
       print returnuid(cdetails, delcontainer)
       try:
            cid = returnuid(cdetails, delcontainer)
            myval = ("docker rm {0}".format(cid))
            delprocess = subprocess.Popen([myval], stdout=subprocess.PIPE, shell=True)
            printsummary()
       except:
           print "Unable to find 2 that container ..."
     
    if containernum.upper() == "P":
        peekcontainer = getcontainer() 
        cpid = getpid(cdetails, peekcontainer)
        foo = terminal2(cpid)
    #printsummary()

    else:
        printsummary()

if __name__ == '__main__':
    printsummary()
