from random import sample, choice
from os import path, makedirs
from time import sleep
import json

# Switch to TCP/MPTCP
# Arguments -
# proto=tcp/mptcp, 					by default it's mptcp
# pmanager=ndiffports/fullmesh
# diffports=N
# delimited by spaces
# payloadsize = 1[KM]

# sample output:
# proto=tcp
#rawArgs = "proto=mptcp pmanager=ndiffports"


# Ensure that logs directory exists in network-tests repository.
# Note that network-tests and mininet-topo-generator should be in the same directory.
directory = "../network-tests/logs/"
filepath = directory + "args.txt"

with open(filepath, 'r') as jsonFile:
	args = json.load(jsonFile)


# Configure the hosts.
for each in net.hosts:
	print "*** Configuring host " + str(each)

	# declare protocol
	cmd = "sysctl -w net.mptcp.mptcp_enabled="
	val = 1 if args['proto'] == "mptcp" else 0
	print "*** Setting protocol to " + args['proto']
	each.cmd(cmd+str(val))

	# declare pmanager if mptcp
	if args['proto'] == "mptcp":
		cmd = "sysctl -w net.mptcp.mptcp_path_manager="
		print "*** Setting path manager to " + args['pmanager']
		each.cmd(cmd+args['pmanager'])

		# configure diffports
		if args['pmanager'] == "ndiffports":
			cmd = "echo \"" + args['diffports'] + "\" | tee /sys/module/mptcp_ndiffports/parameters/num_subflows"
			print "*** Setting diffports to " + args['diffports']
			each.cmd(cmd)

	print ""

if args['payloadsize'] == "query":
	payloadSize = "10K"
elif args['payloadsize'] == "short":
	payloadSize = "500K"
elif args['payloadsize'] == "long": 
	payloadSize = "100M"

runCount = int(args['runcount'])

# Generate randomized sender/receiver pairs.
#  It's a sad day.
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

	# Run multiple iperf runs on the client.
	#   Run is repeated runCount times.
	#   Variable things:
	#     (-n)umber of bytes to transmit n[KM]
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

