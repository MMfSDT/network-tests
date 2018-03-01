from random import sample, choice
from os import path, makedirs
from time import sleep
import json
from subprocess import Popen, PIPE

# Requirements
## Note that network-tests and mininet-topo-generator should be in the same directory.

directory = "../network-tests/logs/"
filepath = directory + "args.txt"

with open(filepath, 'r') as jsonFile:
	args = json.load(jsonFile)


# Network configuration:
print "*** Configuring network"
## Protocol --proto [(mptcp),tcp]
key = "net.mptcp.mptcp_enabled"
val = 1 if args['proto'] == "mptcp" else 0
p = Popen("sysctl -w %s=%s" % (key, val),
		shell=True, stdout=PIPE, stderr=PIPE)
stdout, stderr = p.communicate()
print stdout[:-1]
if len(stderr) != 0:
	print stderr

## Path manager --pmanager [(fullmesh),ndiffports]
if args['proto'] == "mptcp":
	key = "net.mptcp.mptcp_path_manager"
	val = args['pmanager']
	p = Popen("sysctl -w %s=%s" % (key, val),
			shell=True, stdout=PIPE, stderr=PIPE)
	stdout, stderr = p.communicate()
	print stdout[:-1]
	if len(stderr) != 0:
		print stderr

	## Ndiffports --diffports [(1)-16]
	if args['pmanager'] == "ndiffports":
		key = "echo " + args['diffports'] + " | tee /sys/module/mptcp_ndiffports/parameters/num_subflows"
		p = Popen(key, shell=True, stdout=PIPE, stderr=PIPE)
		stdout, stderr = p.communicate()
		print "/sys/module/mptcp_ndiffports/parameters/num_subflows =", stdout[:-1]
		print stderr
		if len(stderr) != 0:
			print stderr

	print ""

## Payload Size --payloadsize [(query),short,long]
### Addendum: Quarter size lonf due to test time
if args['payloadsize'] == "query":
	payloadSize = "10K"
elif args['payloadsize'] == "short":
	payloadSize = "500K"
elif args['payloadsize'] == "long": 
	payloadSize = "25M"

## Run count --runcount [(10),N]
runCount = int(args['runcount'])

# Generate randomized sender/receiver pairs.
length = len(net.hosts)
client = sample(xrange(length), length)

server = []
for each in range(0, length):
	server.append(choice([x for x in client if x not in server]))

	while server[-1] == client[len(server) - 1]:
		server[-1] = choice([x for x in client if x not in server])

print "*** Servers: " + str(server)
print "*** Clients: " + str(client)
print ""

# Iterate through the previously generated server/client pairs.
entries = []
for server, client in zip(server, client):
	# Start iperf on server host (non-blocking).
	serverCmd = "iperf -s &> /dev/null"
	net.hosts[server].sendCmd(serverCmd)

	results = []

	sleep(0.1)
	print "Testing server-client pair " + \
		str(net.hosts[server]) + " " + str(net.hosts[client])
	for each in range(0, runCount):
		clientCmd = "iperf -c" +  net.hosts[server].IP() \
			+ " -n " + payloadSize + " -y c -x CSMV"

		results.append(net.hosts[client].cmd(clientCmd))
		sleep(0.1)


	# JSON FOR LIFE 
	entry = { 'server': str(net.hosts[server]), 'client': str(net.hosts[client]), 'results': [] }
	for each in results:
		entry['results'].append({ 'throughput': int(each.split(",")[-1][:-1].strip()), 'fct': 0 })
	entries.append(entry)

	net.hosts[server].sendInt()
	net.hosts[server].monitor()

# Write it into json dump middle file.
filepath = directory + "mid.json"
with open(filepath, 'w+') as jsonFile:
	json.dump(entries, jsonFile)

print ""
print "Test complete."

