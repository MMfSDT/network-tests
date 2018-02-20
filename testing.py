#!/usr/bin/env python

from os import getcwd
from os.path import abspath, join
from sys import argv
import json

print getcwd(), abspath(".")

# print(net.hosts)
# print 'Globals: ' + str([x for x in globals() if x[0] == 'h']) TODO 

logpath = abspath("../network-tests/logs/")
aggregatefile = join(logpath, "aggregate.json")

with open(aggregatefile, 'w+') as jsonFile:
    print("*** Reading json file from test script.")
    try:
        aggregate = json.load(jsonFile)
    except ValueError:
        aggregate = []
        json.dump(aggregate, jsonFile)
