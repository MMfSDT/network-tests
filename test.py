
from random import sample, choice

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

# fixed values for now. Iteration implementation to follow.
server = 0
client = 1

# Start iperf on server/receiver host (non-blocking).
serverCmd = "iperf -s"
net.hosts[server].sendCmd(serverCmd)

# Run multiple iperf runs on the client/sender.
#   Run is repeated runCount times.
#   Variable things:
#     (-n)umber of bytes to transmit n[KM]
payloadSize = "1K"
runCount = 10
for each in range(0,runCount):
	clientCmd = "iperf -c " +  net.hosts[server].IP() \
		+ " -n " + payloadSize + " -y c -x CSMV"

	print "run #" + str(each)
	print net.hosts[client].cmd(clientCmd)

net.hosts[server].sendInt()
net.hosts[server].monitor()