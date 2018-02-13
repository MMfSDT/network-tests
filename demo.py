
print net.hosts[0] # can access different hosts through this/
print net.hosts[0].cmd("ifconfig") # can be extended like so

from pprint import pprint
pprint(vars(net)) # show the attributes of an object

from random import sample
print sample(net.hosts, 2) # take two samples from a list

# old code
def pickHost(hosts):
	from random import choice
	listlen = len(hosts)

	# choose receiver
	receiver = choice(xrange(listlen))
	while 
		choice(xrange(listlen))

	# choose sender
	choice(xrange(listlen))

print net.hosts[0].IP() # extract IP address of node
