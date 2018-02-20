from random import sample, choice
from time import sleep
from os.path import relpath
from os import getcwd

# generate sender/receiver array
length = len(net.hosts)
receiver = sample(xrange(length), length)

sender = []
for each in range(0, length):
	sender.append(choice([x for x in receiver if x not in sender]))

	while sender[-1] == receiver[len(sender) - 1]:
		sender[-1] = choice([x for x in receiver if x not in sender])

print "senders: " + str(sender)
print "receivers: " + str(receiver)

# Launch server on the corresponding host.
#  Note that sender - server, receiver - client.

payloadSize = "1K"
runCount = 10

# Note that the python script is run within the mininet-topo-generator directory.
# To ensure working code, keep mininet-topo-generator and network-tests on the same directory level
filename = payloadSize + "-" + str(runCount) + ".txt"
f = open("../network-tests/logs/" + filename, "w+")

output = ""
for server,client in zip(sender, receiver):
	# Start iperf on server/receiver host (non-blocking).
	serverCmd = "iperf -s &> /dev/null"
	net.hosts[server].sendCmd(serverCmd)

	# Run multiple iperf runs on the client/sender.
	#   Run is repeated runCount times.
	#   Variable things:
	#     (-n)umber of bytes to transmit n[KM]
	results = []

	sleep(0.001)
	print "Testing server-client pair " + \
		str(net.hosts[server]) + " " + str(net.hosts[client])
	for each in range(0,runCount):
		clientCmd = "iperf -c" +  net.hosts[server].IP() \
			+ " -n " + payloadSize + " -y c -x CSMV"

		results.append(net.hosts[client].cmd(clientCmd))

	# extract average bandwidth
	# Outputs in CSV format <server>,<client>,data
	for each in results:
		f.write(str(net.hosts[server]) + "," + \
			str(net.hosts[client]) + "," + \
			each.split(",")[-1][:-1] + "\n")

	net.hosts[server].sendInt()
	net.hosts[server].monitor()

print "Test complete. Written to " + filename
f.close()