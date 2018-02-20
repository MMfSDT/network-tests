#!/usr/bin/env python

############################################################################################
#   postprocess.py
#       Takes in .pcap files generated within Mininet, as well as iperf throughput results.
#       Follows this syntax:
#           ./postprocess.py 
#       Make sure to set env.sh first before proceeding.
############################################################################################

import json
import re
from os import listdir
from os.path import isfile, join, abspath
from shlex import split
from shutil import copy
from subprocess import check_call, check_output, Popen, PIPE
from sys import exit

topopath = abspath(".") # TODO change this omg
# topopath = abspath("../original-captures/") # TODO change this omg
logpath = abspath("../network-tests/logs/")
midfile = join(topopath, "1K-10.txt")
new_midfile = join(logpath, "1K-10.txt")

def unique (list_):
    # Python cheat to get all unique values in a list.
    return list(set(list_))

def copyPcapFiles ():
    #  Move .pcap logs from topopath to logpath.
    print("*** Copying Mininet .pcap dumps.")
    for file in [join(topopath, f) for f in listdir(topopath) if isfile(join(topopath, f)) and re.search(r'.pcap$', f, re.M)]:
        copy(file, logpath)
    # TODO copy Kyle's output file as well.
    copy(midfile, logpath)

def getInterfaces ():
    # Infer all available interfaces using this code.
    #   Flow: Get all files if it ends with ".pcap", strip and get the interface name (sxdd-ethd), then get all unique values.
    return unique([re.search(r'^(s[eac]\d\d-eth\d)', f, re.M).group(1) for f in listdir(logpath) if isfile(join(logpath, f)) and re.search(r'.pcap$', f, re.M) and re.search(r'^(s[eac]\d\d-eth\d)', f, re.M)])

def mergePcapFiles (interfaces):
    # Merge all _in and _out interfaces.
    print("*** Merging _in and _out pcap files.")
    try:
        [check_call(split("mergecap -w {1}/{0}.pcap {1}/{0}_in.pcap {1}/{0}_out.pcap".format(interface, logpath))) for interface in interfaces]
    except:
        print("*** Failed to merge pcap files. Assuming already merged. Skipping.")

def deleteExcessPcapFiles (interfaces):
    # Delete all _in and _out interfaces, we don't need them anymore.
    print("*** Deleting _in and _out pcap files.")
    try:
        [check_call(split("rm {1}/{0}_in.pcap".format(interface, logpath))) for interface in interfaces]
    except:
        print("*** Failed deleting *_in.pcap files. Assuming already deleted. Skipping.")

    try:
        [check_call(split("rm {1}/{0}_out.pcap".format(interface, logpath))) for interface in interfaces]
    except:
        print("*** Failed deleting *_out.pcap files. Assuming already deleted. Skipping.")

def convertServerToIP (server):
    parsed = [int(x) for x in re.search(r'^h(\d)(\d)(\d)', server, re.M).groups()]
    return '10.{}.{}.{}'.format(parsed[0], parsed[1], parsed[2] + 2)

def getClientInterface (client):
    parsed = [int(x) for x in re.search(r'^h(\d)(\d)(\d)', client, re.M).groups()]
    return '{}/se{}{}-eth{}.pcap'.format(logpath, parsed[0], parsed[1], parsed[2] + 1)

def includeFCT (entries):
    print("*** Extracting FCT from .pcap files.")
    for index, entry in enumerate(entries):
        fcts = Popen(["sh", "-c", 
                "tshark -qz conv,tcp,ip.addr=={} -r {} | sed -e 1,5d | head -n -1 | sort -k 10 -n | awk -F' ' '{{print $11}}'".format(
                    convertServerToIP(entry['server']), 
                    getClientInterface(entry['client'])
                )], stdout=PIPE).communicate()[0].splitlines()

        for index_2, result in enumerate(entry['results']):
            result['fct'] = fcts[index_2]
            entries[index]['results'][index_2] = result
    
    return entries

if '__main__' == __name__:
    copyPcapFiles()
    interfaces = getInterfaces()
    mergePcapFiles(interfaces)
    deleteExcessPcapFiles(interfaces)

    entries = None

    with open(new_midfile, 'r') as jsonFile:
        print("*** Reading json file from test script.")
        entries = json.load(jsonFile)

    entries = includeFCT(entries)

    with open(new_midfile, 'w+') as jsonFile:
        print("*** Writing json file with FCTs.")
        json.dump(entries, jsonFile)
