from os import path, makedirs
from random import sample, choice, uniform
from time import time
from subprocess import Popen, PIPE
from time import sleep
import json

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

## Extract the testing mode
mode = args['mode']
print "*** running test mode " + mode

## Run count --runcount [(10),N]
# runCount = int(args['runcount'])
runCount = 5
portList = [10001, 10002, 10003, 10004, 10005]

length = len(net.hosts)

# We might have to log these down into another log file later on for parsing.
## Indicate the pairing, the time executed, and other pertinent details.

if mode == "onetomany":
	# Generate randomized sender/receiver arrays.
	## two hosts will be isolated in its own array, the rest will be in another
	print "*** changing host directories to ../network-tests/files\n"
	for host in range(0, length):
		if net.hosts[host].cmd("pwd")[-5:] != "files":
			cmd = "cd ../network-tests/files"
			net.hosts[host].cmd(cmd)

	pickList = []
	restList = []

	for x in range(0,5):
		pick = sample(range(0, length), 2)
		pickList.append(pick)

		temp = sample([x for x in range(0, length) if x not in pick], 7)
		restList.append([temp,[x for x in range(0, length) if x not in pick + temp]])

	for run,(pick,rest) in enumerate(zip(pickList, restList)):
		print "*** run " + str(run + 1)
		for i,each in enumerate(pick):
			print str(net.hosts[each]) + " : " + str([str(net.hosts[x]) for x in rest[i] ])
		print ""

	entries = []
	for run,(pick, rest) in enumerate(zip(pickList, restList)):
		print "*** starting simple python servers\n"
		for servers in rest:
			for host in servers:
				cmd = "python -m SimpleHTTPServer " + str(portList[run]) + " &"
				net.hosts[host].cmd(cmd)

		sleep(1)

		print "*** sending requests"
		for host1,host2 in zip(rest[0], rest[1]):
			cmd1 = "wget " + str(net.hosts[host1].IP()) + ":8000/" + args['payloadsize'] + ".out" \
				" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host1]) + " &"
			cmd2 = "wget " + str(net.hosts[host2].IP()) + ":8000/" + args['payloadsize'] + ".out" \
				" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host2]) + " &"

			net.hosts[pick[0]].cmd(cmd1)
			net.hosts[pick[1]].cmd(cmd2)
			print "sent request to " + str(net.hosts[host1]) + " and " + str(net.hosts[host2])

		print "\n*** waiting for clients to finish request"
		for client in pick:
		 	net.hosts[client].monitor()

		print "*** terminating simple python servers\n\n"
		for servers in rest:
			for host in servers:
				net.hosts[host].sendInt()
				net.hosts[host].monitor()

		# Format the results into a json format
		# Load the first pick and its paired rests
		for host in rest[0]:
			entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()), \
					'clientName': str(net.hosts[pick[0]]), 'clientIP': str(net.hosts[pick[0]].IP()), \
					'run': str(portList[run]) \
					}
			entries.append(entry)

		for host in rest[1]:
			entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()), \
					'clientName': str(net.hosts[pick[1]]), 'clientIP': str(net.hosts[pick[1]].IP()), \
					'run': str(portList[run]) \
					}
			entries.append(entry)

	# print entries

elif mode == "onetoone":
	# Generate randomized sender/receiver pairs.
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

		# Format the results into a json format
		entry = { 'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()), \
				'clientName': str(net.hosts[client]), 'serverIP': str(net.hosts[client].IP()), \
				'results': [] }
		for each in results:
			entry['results'].append({ 'throughput': int(each.split(",")[-1][:-1].strip()), 'fct': 0 })
		entries.append(entry)

		net.hosts[server].sendInt()
		net.hosts[server].monitor()

# Write it into json dump middle file.
filepath = directory + "mid.json"
with open(filepath, 'w+') as jsonFile:
	json.dump(entries, jsonFile)



# elif mode == "manytoone":
# 	for run,(pick, rest) in enumerate(zip(pickList, restList)):
# 		print "*** starting simple python servers"
# 		for host in pick:
# 			cmd = "python -m SimpleHTTPServer " + str(portList[run]) + " &"
# 			net.hosts[host].cmd(cmd)

# 		sleep(1)

# 		print "*** sending requests"
# 		for host1,host2 in zip(rest[0], rest[1]):
# 			cmd1 = "wget " + str(net.hosts[pick[0]].IP()) + ":8000/" + args['payloadsize'] + ".out" \
# 				" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host1]) + " &"
# 			cmd2 = "wget " + str(net.hosts[pick[1]].IP()) + ":8000/" + args['payloadsize'] + ".out" \
# 				" -P dump/" + args['payloadsize'] + "-" + str(net.hosts[host2]) + " &"

# 			net.hosts[host1].cmd(cmd1)
# 			net.hosts[host2].cmd(cmd2)
# 			print "sent request from " + str(net.hosts[host1]) + " and " + str(net.hosts[host2])

# 		print "*** waiting for clients to finish request"
# 		for clients in rest:
# 			for host in clients:
# 			 	net.hosts[host].monitor()

# 		print "*** terminating simple python servers"
# 		for server in pick:
# 			net.hosts[server].sendInt()
# 			net.hosts[server].monitor()

# print "*** returning to mininet-topo-generator directory"
# for host in range(0, length):
# 	if net.hosts[host].cmd("pwd")[-9:] != "generator":
# 		cmd = "cd ../../mininet-topo-generator"
# 		net.hosts[host].cmd(cmd)

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


	# Format the results into a json format
	# entry = { 'server': str(net.hosts[server]), 'client': str(net.hosts[client]), 'results': [] }
	# for each in results:
	# 	entry['results'].append({ 'throughput': 0, 'fct': 0 })
	# entries.append(entry)

# 	net.hosts[server].sendInt()
# 	net.hosts[server].monitor()

# entries = []
# for run,(pick,rest) in enumerate(zip(pickList, restList)):
# 	for host1 in pick:
# 		for host2 in rest:
# 			entry = {'pick': str(net.hosts[host1].IP()),\
# 					 'rest': str(net.hosts[host2].IP()),\
# 					 'run': str(portList[run])}
					 
# 		entries.append(entry)

# Write it into json dump middle file.
# filepath = directory + "mid.json"
# with open(filepath, 'w+') as jsonFile:
# 	json.dump(entries, jsonFile)

print "Test complete."

