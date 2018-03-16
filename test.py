from os import path, makedirs
from random import sample, choice
from datetime import datetime
from subprocess import Popen, PIPE
from time import sleep
import json

def time ():
    # Python cheat to get time from Unix epoch
    return int(datetime.now().strftime("%s")) * 1000

# Configuration
## network-tests and mininet-topo-generator should be in the same directory

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
## Each host will be placed into a fixed pair for the entirety of the tests.
length = len(net.hosts)
clients = sample(xrange(length), length/2)

servers = []
for each in range(0, length/2):
	reserved = servers + clients
	servers.append(choice([x for x in range(0, length) if x not in reserved]))

print "*** Server-Client pairs"
for server, client in zip(servers, clients):
	print "*** " + str(net.hosts[server]) + "-" + str(net.hosts[client])
print ""

# We might have to log these down into another log file later on for parsing.
## Indicate the pairing, the time executed, and other pertinent details.

entries = []
# Start iperf on all servers host (non-blocking).
serverCmd = "iperf -s &> /dev/null"
for host in servers:
	net.hosts[host].sendCmd(serverCmd)

print "*** starting iperf servers..."
print ""
sleep(1)

for client, server in zip(clients, servers):
	# Append time into the log file
	clientCmd = "iperf -c" + net.hosts[server].IP() + " -n " + "1" + " -y c -x CSMV" \
	+ " >> ../network-tests/logs/tp/" + str(net.hosts[client]) + "-log"
	net.hosts[client].sendCmd(clientCmd)

# Wait for the senders to finish before closing them
for host in clients:
	net.hosts[host].monitor()

for host in servers:
	print "*** stopping host " + str(net.hosts[host])
	net.hosts[host].sendInt()
	net.hosts[host].monitor()

# for server, client in zip(server, client):
	
# 	serverCmd = "iperf -s &> /dev/null"
# 	net.hosts[server].sendCmd(serverCmd)

# 	results = []

# 	sleep(0.1)
# 	print "Testing server-client pair " + \
# 		str(net.hosts[server]) + " " + str(net.hosts[client])
# 	for each in range(0, runCount):
# 		clientCmd = "iperf -c" +  net.hosts[server].IP() \
# 			+ " -n " + payloadSize + " -y c -x CSMV"

# 		results.append(net.hosts[client].cmd(clientCmd))
# 		sleep(0.1)


# 	# Format the results into a json format
# 	entry = { 'server': str(net.hosts[server]), 'client': str(net.hosts[client]), 'results': [] }
# 	for each in results:
# 		entry['results'].append({ 'throughput': int(each.split(",")[-1][:-1].strip()), 'fct': 0 })
# 	entries.append(entry)

# 	net.hosts[server].sendInt()
# 	net.hosts[server].monitor()

# # Write it into json dump middle file.
# filepath = directory + "mid.json"
# with open(filepath, 'w+') as jsonFile:
# 	json.dump(entries, jsonFile)

print ""
print "Test complete."

