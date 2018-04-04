from os import path, makedirs
from random import sample, choice, uniform
from time import time
from subprocess import Popen, PIPE
from time import sleep
import json

test = "onetomany"

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
### Set maximum time for test
# Note that these payloads are in MiB, KiB
if args['payloadsize'] == "query":
	payloadSize = "10K"
elif args['payloadsize'] == "short":
	payloadSize = "500K"
elif args['payloadsize'] == "long": 
	payloadSize = "25M"

## Run count --runcount [(10),N]
runCount = int(args['runcount'])

# Generate randomized sender/receiver arrays.
## two hosts will be isolated in its own array, the rest will be in another
length = len(net.hosts)
clients = sample(xrange(length), 1)

servers = range(0, length)
for host in clients:
	servers.remove(host)

print "*** Servers: "
for server in servers:
	print str(net.hosts[server])
print "*** Clients: "
for client in clients:
	print str(net.hosts[client])

print ""

# We might have to log these down into another log file later on for parsing.
## Indicate the pairing, the time executed, and other pertinent details.

if test == "onetomany":
	# Transfer directories to network-tests/files where the payloads are 
	print "*** changing directories"
	cmd = "cd ../network-tests/files"
	net.hosts[clients[0]].cmd(cmd)

	# Start SimpleHTTPServer an all servers
	print "*** starting servers"
	for host in servers:
		# Make sure all hosts in the servers list have changed directories
		if net.hosts[host].cmd("pwd")[-5:] != "files":
			cmd = "cd ../network-tests/files"
			net.hosts[host].cmd(cmd)

		cmd = "python -m SimpleHTTPServer &> /dev/null"
		net.hosts[host].sendCmd(cmd)

	sleep(1)

	# Begin the file transfer
	# Ip address, port, file for the wget command
	print "*** sending requests"
	for each in servers:
		# cmd = "wget " + str(net.hosts[each].IP()) + ":8000/" + args['payloadsize'] + ".out" \
		# 	" -P dump/" + args['payloadsize'] + "-" + str(each) + ".out"
		
		cmd = "wget " + str(net.hosts[each].IP()) + ":8000/" + args['payloadsize'] + ".out" + \
			" -P dump/ &"

		print "Sending request to " + str(net.hosts[each])
		net.hosts[clients[0]].cmd(cmd)

	for host in clients:
		net.hosts[host].monitor()

	## Works until here.

	for host in servers:
		print "*** stopping host " + str(net.hosts[host])
		net.hosts[host].sendInt()
		while net.hosts[host].waiting != False:
			pass

		# net.hosts[host].monitor()	## does not terminate properly

# elif test == "manytoone":
# 	# Transfer directories to network-tests/files where the payloads are 
# 	print "*** changing directories"
# 	cmd = "cd ../network-tests/files"
# 	net.hosts[clients[0]].cmd(cmd)

# 	# Ensure that all the nodes have transfered directories
# 	for host in servers:
# 		if net.hosts[host].cmd("pwd")[-5:] != "files":
# 			cmd = "cd ../network-tests/files"
# 			net.hosts[host].cmd(cmd)

# 	sleep(1)

# 	for each in servers:
# 		cmd = "wget " + str(net.hosts[clients[0]].IP()) + ":8000/" + args['payloadsize'] + ".out" + \
# 			" -P dump/ &" 

# 		print "Sending request from " + str(net.hosts[each])
# 		net.hosts[each].cmd(cmd)

# 	for host in clients:
# 		print "*** waiting for sending"
# 		net.hosts[host].monitor()

# 	for host in servers:
# 		print "*** stopping host " + str(net.hosts[host])
# 		net.hosts[host].sendInt()
# 		net.hosts[host].monitor()	## does not terminate properly

# if testingInterval != "random":
# 	# Start iperf on all servers host (non-blocking).
# 	serverCmd = "iperf -s &> /dev/null"
# 	for host in servers:
# 		net.hosts[host].sendCmd(serverCmd)

# 	print "*** starting iperf servers..."
# 	print ""
# 	sleep(1)

# 	for client, server in zip(clients, servers):
# 		# Append time into the log file
# 		clientCmd = "iperf -c" + net.hosts[server].IP() + " -n " + "1" + " -y c -x CSMV" \
# 		+ " >> ../network-tests/logs/tp/" + str(net.hosts[client]) + "-log"
# 		net.hosts[client].sendCmd(clientCmd)

# else:
# 	print "potato"
# 	serverCmd = "iperf -s &> /dev/null"
# 	for host in servers:
# 		net.hosts[host].sendCmd(serverCmd)

# 	print "*** starting iperf servers..."
# 	print ""
# 	sleep(1)

# 	endTime = time() + testingTime
# 	clientQueue = clients
# 	# Start the randomization process
# 	while time() < endTime:
# 		if len(clientQueue) != 0:
# 			client = sample(clientQueue, 1)[0]
# 			clientQueue.remove(client)
# 		else:
# 			break

# 		clientCmd = "iperf -c" + net.hosts[servers[clients.index(client)]].IP() + " -n " + "1" + " -y c -x CSMV" \
# 		+ " >> ../network-tests/logs/tp/" + str(net.hosts[client]) + "-log"
# 		net.hosts[client].sendCmd(clientCmd)

# 		waitInterval = uniform(0, testingTime/len(clients))
# 		sleep(waitInterval)

	# # Wait for the senders to finish before closing them
	# for host in clients:
	# 	net.hosts[host].monitor()

	# for host in servers:
	# 	print "*** stopping host " + str(net.hosts[host])
	# 	net.hosts[host].sendInt()
	# 	net.hosts[host].monitor()

# Clear test files in dump

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

