from os import path, makedirs
from random import sample, choice, uniform
from time import time
from subprocess import Popen, PIPE
from time import sleep
import json

test = "manytoone"

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
clients = sample(xrange(length), 2)

servers = range(0, length)
for host in clients:
	servers.remove(host)

servers_0 = sample(servers, (length -2)/2)
servers_1 = [x for x in servers if x not in servers_0]

server_set = [servers_0, servers_1]

print "*** Servers: "
for servers in server_set:
	print [str(net.hosts[x]) for x in servers]

print "*** Clients: "
print [str(net.hosts[x]) for x in clients]

print ""

# We might have to log these down into another log file later on for parsing.
## Indicate the pairing, the time executed, and other pertinent details.

print "*** changing host directories to ../network-tests/files"
for host in range(0, length):
	if net.hosts[host].cmd("pwd")[-5:] != "files":
		cmd = "cd ../network-tests/files"
		net.hosts[host].cmd(cmd)

if test == "onetomany":
	print "*** starting simple python servers"
	for servers in server_set:
		for host in servers:
			cmd = "python -m SimpleHTTPServer &"
			net.hosts[host].cmd(cmd)

	sleep(1)

	print "*** sending requests"
	for host1,host2 in zip(server_set[0], server_set[1]):
		cmd1 = "wget " + str(net.hosts[host1].IP()) + ":8000/" + args['payloadsize'] + ".out" \
			" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host1]) + " &"
		cmd2 = "wget " + str(net.hosts[host2].IP()) + ":8000/" + args['payloadsize'] + ".out" \
			" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host2]) + " &"

		net.hosts[clients[0]].cmd(cmd1)
		net.hosts[clients[1]].cmd(cmd2)
		print "sent request to " + str(net.hosts[host1]) + " and " + str(net.hosts[host2])

	print "*** waiting for clients to finish request"
	for host in clients:
	 	net.hosts[host].monitor()

	print "*** terminating simple python servers"
	for servers in server_set:
		for host in servers:
			net.hosts[host].sendInt()
			net.hosts[host].monitor()

elif test == "manytoone":
	print "*** starting simple python servers"
	for host in clients:
		cmd = "python -m SimpleHTTPServer &"
		net.hosts[host].cmd(cmd)

	sleep(1)

	print "*** sending requests"
	for host1,host2 in zip(server_set[0], server_set[1]):
		cmd = "wget " + str(net.hosts[clients[0]].IP()) + ":8000/" + args['payloadsize'] + ".out" \
			" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host1]) + " &"
		cmd = "wget " + str(net.hosts[clients[1]].IP()) + ":8000/" + args['payloadsize'] + ".out" \
			" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host2]) + " &"

		net.hosts[host1].cmd(cmd1)
		net.hosts[host2].cmd(cmd2)
		print "sent request from " + str(net.hosts[host1]) + " and " + str(net.hosts[host2])

	print "*** waiting for clients to finish request"
	for servers in server_set:
		for host in servers:
		 	net.hosts[host].monitor()

	print "*** terminating simple python servers"
	for host in clients:
		net.hosts[host].sendInt()
		net.hosts[host].monitor()

print "*** returning to mininet-topo-generator directory"
for host in range(0, length):
	if net.hosts[host].cmd("pwd")[-9:] != "generator":
		cmd = "cd ../../mininet-topo-generator"
		net.hosts[host].cmd(cmd)

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
# 		entry['results'].append({ 'throughput': 0, 'fct': 0 })
# 	entries.append(entry)

# # 	net.hosts[server].sendInt()
# # 	net.hosts[server].monitor()

# # Write it into json dump middle file.
# filepath = directory + "mid.json"
# with open(filepath, 'w+') as jsonFile:
# 	json.dump(entries, jsonFile)

print ""
print "Test complete."

