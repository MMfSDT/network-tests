from random import sample, choice
from os import path, makedirs
from time import sleep
import json

# Switch to TCP/MPTCP
# Arguments -
# proto=tcp/mptcp, 					by default it's mptcp
# pmanager=ndiffports/fullmesh
# ports=N
# delimited by spaces
# payloadsize = 1[KM]

# sample output:
# proto=tcp
#rawArgs = "proto=mptcp pmanager=ndiffports"
#rawArgs.split(" ")

#args = dict()

#proto, pmanager, ports, payloadsize, runcount

payloadSize = "1K"
runCount = 10

# generate sender/receiver array
#  Note that sender - server, receiver - client.
length = len(net.hosts)
receiver = sample(xrange(length), length)

sender = []
for each in range(0, length):
	sender.append(choice([x for x in receiver if x not in sender]))

	while sender[-1] == receiver[len(sender) - 1]:
		sender[-1] = choice([x for x in receiver if x not in sender])

print "senders: " + str(sender)
print "receivers: " + str(receiver)


# Ensure that logs directory exists in network-tests repository.
# Note that network-tests and mininet-topo-generator should be in the same directory.
directory = "../network-tests/logs/"
if not path.exists(directory):
	print "Created logs directory."
	makedirs(directory)

filepath = directory + "mid.json" 


# Iterate through the previously generated sender/receiver pairs.
entries = []
for server, client in zip(sender, receiver):
	# Start iperf on server/receiver host (non-blocking).
	serverCmd = "iperf -s &> /dev/null"
	net.hosts[server].sendCmd(serverCmd)

	# Run multiple iperf runs on the client/sender.
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

	# extract average bandwidth
	# Outputs in CSV format <server>,<client>,data
	# for each in results:
	# 	f.write(str(net.hosts[server]) + "," + \
	# 		str(net.hosts[client]) + "," + \
	# 		each.split(",")[-1][:-1] + "\n")

	# JSON FOR LIFE 
	entry = { 'server': str(net.hosts[server]), 'client': str(net.hosts[client]), 'results': [] }
	for each in results:
		entry['results'].append({ 'throughput': int(each.split(",")[-1][:-1].strip()), 'fct': 0 })
	entries.append(entry)

	net.hosts[server].sendInt()
	net.hosts[server].monitor()

with open(filepath, 'w+') as jsonFile:
	json.dump(entries, jsonFile)

print "Test complete. Parameters: "