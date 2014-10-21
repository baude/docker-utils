import os
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


    def checkcontaineruid(self):
        """Checks ID and returns valid containeruid. Accepts partial UID"""
        proc = subprocess.Popen(["docker ps -q"],
                                stdout=subprocess.PIPE, shell=True)
        out = proc.stdout.read()
        containeruids = out.split()
        if not len(self.cuid) >= 3:
            print "Container ID must be at least 3 characters"
            quit()
        else:
            match = [containeruid for containeruid in containeruids if re.match(self.cuid, containeruid)]
            if match:
                 return match[0]
            else:
                print "Unable to find container ID '%s'. Try 'docker ps'." % self.cuid
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
        dockjson = self.container_json
        newjson = dict
        newconfig = []
        newhost = dict

        configkeys = {'Config': {'AttachStderr', 'AttachStdin', 'AttachStdout',
                                 'Cmd', 'CpuShares', 'Cpuset', 'Env', 'Hostname',
                                 'Image', 'Memory', 'Tty', 'User', 'WorkingDir'
                                 },
                      'HostConfig': {'Binds', 'CapAdd', 'CapDrop', 'ContainerIDFile', 'Dns',
                                     'DnsSearch', 'Links', 'LxcConf', 'NetworkMode',
                                     'PortBindings', 'Privileged', 'PublishAllPorts'
                                     }
                      }

        vals = self.assembledict(newconfig, configkeys, dockjson)
        self.writeoutput(vals)

    def kubernetes_file(self):
        _kube = self.outname.replace('.json', '-pod.json')
        _schema = self.kube_schema
        _schema.update({"id": "foobar"})
        #print json.dumps(_schema, indent=2, sort_keys=False)
        print "Wrote kube file %s" % _kube
        #def assembledict(self, mydict, mykeys, dockjson):
        #    userdict = {'UserParams': {'restart': '', 'rm': '' , 'dockercommand': '',
        #                             'sig-proxy':''
        #                            }}
        #    for desc in mykeys:
        #        newdict = {desc: {}}
        #        for keys in mykeys[desc]:
        #            newdict[desc][keys] = dockjson[desc][keys]
        #        mydict.append(newdict)
        #    if dockjson['Name'] != "":
        #        namedict = {'Name': dockjson['Name'] }
        #        mydict.append(namedict)
        #    mydict.append(userdict)
        #    return mydict

    @property
    def kube_schema(self):
        kube = {
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
        return kube

class List(object):
    def __init__(self, local):
        self.local = local
        self.templates_dir = "/var/container-templates/"
        self.pattern = 'json$'

    def metadata_files(self):
        dirlist = [self.templates_dir]
        if self.local:
            dirlist.append('.')
        files = [f for d in dirlist for f in os.listdir(d) if re.search(self.pattern, f)]
        for f in files:
            print f

class Pull(object):
    def __init__(self, outfile, install, force):
        self.install = install
        self.force = force
        self.templates_dir = "/var/container-templates"
        self.outfile = outfile
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
        if self.install:
            return "{0}/{1}".format(self.templates_dir, filename)
        else:
            return "{0}".format(filename)

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
            print ("{0} already exists. You can pass -f to override".format(self.outname))
            quit()
        else:
            with open(self.outname, "w") as outfile:
                outfile.write(self.response.read())
            outfile.closed
            print ("Wrote {0}".format(self.outname))
