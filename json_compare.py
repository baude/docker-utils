import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--base", help="basefile")
parser.add_argument("-d", "--delta", help="deltafile")
args = parser.parse_args()
fname1 = args.base
fname2 = args.delta

file1 = json.loads(open(fname1).read())
file2 = json.loads(open(fname2).read())

mydict = file1[0]
mydict2 = file2[0]

def iterkey(key, thedict):
    global mydict
    for k,v in thedict.iteritems():
        if mydict[key][k] != mydict2[key][k]:
            if mydict[key][k] == "":
                dict1val = "None"
            else:
                dict1val = mydict[key][k]
            if mydict2[key][k] == "":
                dict2val = "None"
            else:
                dict2val = mydict2[key][k]
            print "{0} {1} vs {2}".format(k, dict1val, dict2val)

for k, v in mydict.iteritems():
    if type(mydict[k]) == dict:
        iterkey(k, mydict[k])
    else:
        if mydict[k] != mydict2[k]:
            if mydict[k] == "":
                dict1val = "None"
            else:
                dict1val = mydict[k]
            if mydict2[k] == "":
                dict2val = "None"
            else:
                dict2val = mydict2[k]
            print "{0} {1} vs {2}".format(k, dict1val, dict2val)



