#!/usr/bin/env python
# pylint: disable-msg=C0103,E0602,C0301,C0111,C0325,W0621,W0702

############################################################################################
#   postprocess.py
#       Takes in .pcap files generated within Mininet, as well as iperf throughput results.
#       Follows this syntax:
#           ./postprocess.py
#       Make sure to set env.sh first before proceeding.
############################################################################################

import json
import re
from datetime import datetime
from time import strptime, strftime, localtime
from os import listdir, makedirs
from os.path import isfile, join, abspath
from shlex import split
from shutil import copy
from subprocess import check_call, Popen, PIPE
import errno
import sqlite3


def unique(list_):
    # Python cheat to get all unique values in a list.
    return list(set(list_))


def time():
    # Python cheat to get time from Unix epoch
    return int(datetime.now().strftime("%s")) * 1000

def isoToDateTime(timeString):
    # Expects 'YYYY-MM-DD HH:MM:SS'
    return datetime(*strptime(timeString, '%Y-%m-%d %H:%M:%S')[:6])

def millisToISO(millis):
    return strftime('%Y-%m-%d %H:%M:%S', localtime(millis / 1000.0))


topopath = abspath(".")
logpath = abspath("../network-tests/logs/")
standardtime = time()
isoStandard = millisToISO(standardtime)
pcappath = abspath("../network-tests/logs/pcaps/pcap-{}".format(standardtime))
dbpath = abspath("../network-tests/logs/aggregate.db")
midfile = join(logpath, "mid.json")
argsfile = join(logpath, "args.txt")


def copyPcapFiles():
    # Move .pcap logs from topopath to logpath.
    print("*** Copying Mininet .pcap dumps.")
    # Make pcap directory.
    try:
        makedirs(pcappath)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise

    for pcapFile in [join(topopath, f) for f in listdir(topopath)
                     if isfile(join(topopath, f)) and re.search(r'.pcap$', f, re.M)]:
        copy(pcapFile, pcappath)


def getInterfaces():
    # Infer all available interfaces using this code.
    #   Flow: Get all files if it ends with ".pcap", strip and get the interface name (sxdd-ethd), then get all unique values.
    return unique([re.search(r'^(s[eac]\d\d-eth\d)', f, re.M).group(1) for f in listdir(pcappath) if isfile(join(pcappath, f)) and re.search(r'.pcap$', f, re.M) and re.search(r'^(s[eac]\d\d-eth\d)', f, re.M)])


def mergePcapFiles(interfaces):
    # Merge all _in and _out interfaces.
    print("*** Merging _in and _out pcap files.")
    try:
        [check_call(split("mergecap -w {1}/{0}.pcap {1}/{0}_in.pcap {1}/{0}_out.pcap".format(
            interface, pcappath))) for interface in interfaces]
    except:
        print("*** Failed to merge pcap files. Assuming already merged. Skipping.")


def deleteExcessPcapFiles(interfaces, savePcaps):
    # Delete all _in and _out interfaces, we don't need them anymore.
    print("*** Deleting _in and _out pcap files.")
    try:
        [check_call(split("rm {1}/{0}_in.pcap".format(interface, pcappath)))
         for interface in interfaces]
    except:
        print("*** Failed deleting *_in.pcap files. Assuming already deleted. Skipping.")

    try:
        [check_call(split("rm {1}/{0}_out.pcap".format(interface, pcappath)))
         for interface in interfaces]
    except:
        print("*** Failed deleting *_out.pcap files. Assuming already deleted. Skipping.")

    if savePcaps == "false":
        print("*** Removing entire .pcap folder (no `--pcap` argument).")
        try:
            check_call(split("rm -rf {}".format(pcappath)))
        except:
            print("*** Failed deleting *.pcap files. Assuming already deleted. Skipping.")
    else:
        print("*** Leaving some .pcaps (`--pcap`).")


def convertHostToIP(host):
    parsed = [int(x)
              for x in re.search(r'^h(\d+)(\d+)(\d+)', host, re.M).groups()]
    return '10.{}.{}.{}'.format(parsed[0], parsed[1], parsed[2] + 2)

def convertIPtoHost(ip):
    parsed = [int(x) for x in re.search(r'^10.(\d).(\d).(\d)', ip, re.M).groups()]
    return 'h{}{}{}'.format(parsed[0], parsed[1], parsed[2] - 2)

def getClientInterface(client):
    parsed = [int(x)
              for x in re.search(r'^h(\d)(\d)(\d)', client, re.M).groups()]
    return '{}/se{}{}-eth{}.pcap'.format(pcappath, parsed[0], parsed[1], parsed[2] + 1)

def setupDatabase():
    db = sqlite3.connect(dbpath)
    c = db.cursor()
    # c.execute('''create table if not exists metadata (router text not null, K integer not null, proto text not null, pmanager text not null, diffports integer not null, juggler text not null, payloadsize text not null, runcount integer not null, mode text not null, postprocessedTimestamp text not null);''')
    c.execute('''create table if not exists metadata (router text not null, K integer not null, proto text not null, pmanager text not null, diffports integer not null, juggler text not null, payloadsize text not null, runcount integer not null, mode text not null, postprocessedTimestamp text not null, UNIQUE(postprocessedTimestamp));''')
    c.execute('''create table if not exists instances (switch text not null, interface text not null, sourceHost text not null, destinationHost text not null, sourceIP text not null, sourcePort integer not null, destinationIP text not null, destinationPort integer not null, bytesToSource integer not null, bytesToDest integer not null, timestamp text not null, duration real not null, instanceMetadata integer, FOREIGN KEY(instanceMetadata) REFERENCES metadata(rowid));''')
    db.commit()
    return (db, c)

def closeDatabase(db):
    db.close()

def processPcaps(db, c, interfaces):
    args = None
    metadataId = None

    with open(argsfile, 'r') as jsonFile:
        print("*** Reading args.txt file from test script.")
        args = json.load(jsonFile)
        args['timestamp'] = standardtime
        print("*** Using the following test arguments:")
        print(json.dumps(args, indent=4, sort_keys=True))

        c.execute('insert into metadata (router, K, proto, pmanager, diffports, juggler, payloadsize, runcount, mode, postprocessedTimestamp) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (args["router"], args["K"], args["proto"], args["pmanager"], args["diffports"], args["juggler"], args["payloadsize"], args["runcount"], args["mode"], isoStandard))
        metadataId = c.lastrowid

    print("*** Extracting flow information from .pcap files.")

    for switchInterface in interfaces:
        (switch, interface) = switchInterface.split('-')
        flowInfo = Popen(["sh", "-c", "tshark -t ad -qz conv,tcp -r {}.pcap | sed -E -e 1,5d -e 's/:/ /' -e 's/:/ /' | head -n -1 | sort -k 12 | awk -F' ' '{{print $1 \",\" $2 \",\" $4 \",\" $5 \",\" $7 \",\" $9 \",\" $12 \" \" $13 \",\" $14}}'".format("{}/{}".format(pcappath, switchInterface))], stdout=PIPE).communicate()[0].splitlines()
        # print flowInfo

        for commaDelimited in flowInfo:
            rest = commaDelimited.split(',')
            sourceHost = convertIPtoHost(rest[0])
            destinationHost = convertIPtoHost(rest[2])
            queryArgs = [switch, interface, sourceHost, destinationHost] + rest + [metadataId]

            # Dirty typecasting.
            queryArgs[5] = int(queryArgs[5])
            queryArgs[7] = int(queryArgs[7])
            queryArgs[8] = int(queryArgs[8])
            queryArgs[9] = int(queryArgs[9])
            queryArgs[11] = float(queryArgs[11])

            queryArgs = tuple(queryArgs)

            c.execute('insert into instances (switch, interface, sourceHost, destinationHost, sourceIP, sourcePort, destinationIP, destinationPort, bytesToSource, bytesToDest, timestamp, duration, instanceMetadata) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', queryArgs)

    db.commit()
    return args["pcap"]

if __name__ == '__main__':
    print("")
    copyPcapFiles()
    interfaces = getInterfaces()
    mergePcapFiles(interfaces)
    (db, c) = setupDatabase()
    savePcaps = processPcaps(db, c, interfaces)
    deleteExcessPcapFiles(interfaces, savePcaps)
    closeDatabase(db)

