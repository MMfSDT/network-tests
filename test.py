# pylint: disable-msg=C0103,E0602,C0301,C0111

# from os import path, makedirs, environ
# from random import sample, choice, uniform
from random import sample, choice
from subprocess import Popen, PIPE, STDOUT
from time import sleep, time
# from mininet.util import pmonitor
import shlex
import json

# Configuration
# network-tests and mininet-topo-generator should be in the same directory

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
if not stderr:
    print stderr

# Path manager --pmanager [(fullmesh),ndiffports]
if args['proto'] == "mptcp":
    key = "net.mptcp.mptcp_path_manager"
    val = args['pmanager']
    p = Popen("sysctl -w %s=%s" % (key, val),
              shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    print stdout[:-1]
    if not stderr:
        print stderr

    ## Ndiffports --diffports [(1)-16]
    if args['pmanager'] == "ndiffports":
        key = "echo " + args['diffports'] + \
            " | tee /sys/module/mptcp_ndiffports/parameters/num_subflows"
        p = Popen(key, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        print "/sys/module/mptcp_ndiffports/parameters/num_subflows =", stdout[:-1]
        print stderr
        if not stderr:
            print stderr

    print ""

# Payload Size --payloadsize [(query),short,long]
# Addendum: Quarter size lonf due to test time
# Set maximum time for test
# Note that these payloads are in MiB, KiB
if args['payloadsize'] == "query":
    payloadSize = "10K"
elif args['payloadsize'] == "short":
    payloadSize = "500K"
elif args['payloadsize'] == "long":
    payloadSize = "25M"

# Extract args
mode = args['mode']
runCount = int(args['runcount'])
K = int(args['K'])

print "*** running test mode {}".format(mode)


def getPort(currentRun):
    startRangePort = 50000
    return startRangePort + currentRun


length = len(net.hosts)

# We might have to log these down into another log file later on for parsing.
# Indicate the pairing, the time executed, and other pertinent details.

if mode == "onetomany":
    # Generate randomized sender/receiver arrays.
    # two hosts will be isolated in its own array, the rest will be in another
    if K < 4:
        raise ValueError('### ERROR: onetomany does not work on K < 4.')

    print "*** changing host directories to ../network-tests/files\n"
    for host in range(0, length):
        if net.hosts[host].cmd("pwd")[-5:] != "files":
            cmd = "cd ../network-tests/files"
            net.hosts[host].cmd(cmd)

    pickList = []
    restList = []

    for x in range(0, runCount):
        pick = sample(range(0, length), 2)
        pickList.append(pick)

        temp = sample([x for x in range(0, length)
                       if x not in pick], (length - 2) / 2)
        restList.append(
            [temp, [x for x in range(0, length) if x not in pick + temp]])

    for run, (pick, rest) in enumerate(zip(pickList, restList)):
        print "*** run {}".format(run)
        for i, each in enumerate(pick):
            print str(net.hosts[each]) + " : " + \
                str([str(net.hosts[x]) for x in rest[i]])
        print ""

    entries = []
    timestamp = int(time())

    for run, (pick, rest) in enumerate(zip(pickList, restList)):
        print "*** Run #{}: starting HTTP Python servers\n".format(run)

        # Prepare the command to run within the nodes.
        # The first few spaces in the beginning is necessary as either Bash or Python removes the first character sometimes.
        cmd = "  python -m SimpleHTTPServer {} &".format(getPort(run))
        # sendCmd() and waitOutput() runs and prints the script output.
        expectedOutput = "Serving HTTP on 0.0.0.0 port {} ...".format(getPort(run))

        for servers in rest:
            for host in servers:
                # We'll be using a simple backoff algorithm to ensure that our servers are running.
                backoff = 0.1
                retries = 0
                maxRetries = 3

                while retries < maxRetries:
                    net.hosts[host].sendCmd(cmd)
                    sleep(backoff * (retries + 1))

                    output = net.hosts[host].waitOutput()

                    # Uncomment these lines for further debugging.
                    # print output
                    # print expectedOutput in output

                    if expectedOutput in output:
                        print "Host {} is up.".format(net.hosts[host])
                        break
                    else:
                        # Print the error message if it fails.
                        print output
                        retries = retries + 1

                # If the error persists, stop testing, and mark the test as a failure.
                if retries == maxRetries:
                    raise ValueError("Can't start server within node.")

        print "\n*** Run #{}: sending requests".format(run)

        client_popens = []
        for host1, host2 in zip(rest[0], rest[1]):
            # I'm sorry Kyle. I switched to curl because I thought wget wasn't working properly.
            cmd1 = "curl -v http://{}:{}/{}.out --retry 3 --retry-connrefused -o /tmp/mmfsdt-{}-run{}-{}-{}".format(net.hosts[host1].IP(), getPort(run), args['payloadsize'], timestamp, run, args['payloadsize'], net.hosts[host1])
            cmd2 = "curl -v http://{}:{}/{}.out --retry 3 --retry-connrefused -o /tmp/mmfsdt-{}-run{}-{}-{}".format(net.hosts[host2].IP(), getPort(run), args['payloadsize'], timestamp, run, args['payloadsize'], net.hosts[host2])

            client_popens.append({"from": net.hosts[pick[0]], "to": net.hosts[host1], "command": cmd1, "process": net.hosts[pick[0]].popen(shlex.split(cmd1), stderr=STDOUT)})
            client_popens.append({"from": net.hosts[pick[1]], "to": net.hosts[host2], "command": cmd2, "process": net.hosts[pick[1]].popen(shlex.split(cmd2), stderr=STDOUT)})

            print "sent request to {} and {}".format(net.hosts[host1], net.hosts[host2])

        print "\n*** Run #{}: waiting for clients to finish request".format(run)

        for p in client_popens:
            (out, err) = p["process"].communicate()
            for item in out.split("\n"):
                if "curl: " in item:
                    print "!!! Download error."
                    print item.strip()
                    print ""
                    print "*** *** Output"
                    print out.strip()
                    print ""
                    print ">>> >>> from: {}; to: {}; command: {}".format(p["from"], p["to"], p["command"])
                    raise ValueError("Download error. Retry test.")

        print "*** Run #{}: terminating simple python servers\n\n".format(run)
        for servers in rest:
            for host in servers:
                net.hosts[host].sendInt()
                net.hosts[host].monitor()

        # Format the results into a json format
        # Load the first pick and its paired rests
        for server in rest[0]:
            # print server
            entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()),
                     'clientName': str(net.hosts[pick[0]]), 'clientIP': str(net.hosts[pick[0]].IP()),
                     'run': str(getPort(run))
                    }
            # print entry
            entries.append(entry)

        for server in rest[1]:
            entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()),
                     'clientName': str(net.hosts[pick[1]]), 'clientIP': str(net.hosts[pick[1]].IP()),
                     'run': str(getPort(run))
                    }
            entries.append(entry)

    # print entries

elif mode == "onetoone":
    # Generate randomized sender/receiver pairs.
    clients = sample(xrange(length), length)

    servers = []
    for each in range(0, length):
        servers.append(choice([x for x in clients if x not in servers]))

        while servers[-1] == clients[len(servers) - 1]:
            servers[-1] = choice([x for x in clients if x not in servers])

    print "*** Servers: " + str(servers)
    print "*** Clients: " + str(clients)
    print ""

    # Iterate through the previously generated server/client pairs.
    entries = []

    for run in range(0, runCount):
        print "*** Run #{}: starting iperf servers.".format(run)

        # Prepare the command to run within the nodes.
        # The first few spaces in the beginning is necessary as either Bash or Python removes the first character sometimes.
        serverCmd = "  iperf -s -p {} &".format(getPort(run))
        # sendCmd() and waitOutput() runs and prints the script output.
        expectedOutput = "Server listening on TCP port {}".format(getPort(run))

        for server in servers:
            # We'll be using a simple backoff algorithm to ensure that our servers are running.
            backoff = 0.1
            retries = 0
            maxRetries = 3

            while retries < maxRetries:
                net.hosts[server].sendCmd(serverCmd)
                sleep(backoff * (retries + 1))

                output = net.hosts[server].waitOutput()

                # Uncomment these lines for further debugging.
                # print output
                # print expectedOutput in output

                if expectedOutput in output:
                    print "Host {} is up.".format(net.hosts[server])
                    break
                else:
                    # Print the error message if it fails.
                    print output
                    retries = retries + 1

            # If the error persists, stop testing, and mark the test as a failure.
            if retries == maxRetries:
                raise ValueError("Can't start server within node.")

        # # Start iperf on server on port <run>
        # for server in servers:
        #     serverCmd = "iperf -s -p {} &".format(getPort(run))
        #     # serverCmd = "iperf -s -p {} &> /dev/null".format(getPort(run))
        #     net.hosts[server].sendCmd(serverCmd)
        #     print net.hosts[server].waitOutput()
        #     sleep(0.1)

        print "*** Run #{}: sending requests".format(run)

        for server, client in zip(servers, clients):

            # Prepare the command to run within the nodes.
            # The first few spaces in the beginning is necessary as either Bash or Python removes the first character sometimes.
            clientCmd = "iperf -c {} -n {} -p {} -y c -x CSMV".format(net.hosts[server].IP(), payloadSize, getPort(run))
            # sendCmd() and waitOutput() runs and prints the script output.
            expectedOutput = "Server listening on TCP port {}".format(getPort(run))

            # We'll be using a simple backoff algorithm to ensure that our servers are running.
            backoff = 0.1
            retries = 0
            maxRetries = 3

            while retries < maxRetries:
                net.hosts[client].sendCmd(clientCmd)
                sleep(backoff * (retries + 1))

                output = net.hosts[client].waitOutput()

                # Uncomment these lines for further debugging.
                # print output
                # print expectedOutput in output

                if len([i for i, letter in enumerate(output) if letter == ","]) == 8:
                    print "{}-{} succeeeded.".format(net.hosts[server], net.hosts[client])
                    break
                else:
                    # Print the error message if it fails.
                    print output
                    retries = retries + 1

            # If the error persists, stop testing, and mark the test as a failure.
            if retries == maxRetries:
                raise ValueError("Failed iperf with {}-{}".format(net.hosts[server], net.hosts[client]))

            entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()),
                     'clientName': str(net.hosts[client]), 'clientIP': str(net.hosts[client].IP()),
                     'run': str(getPort(run))
                    }
            entries.append(entry)

        print "*** Run #{}: quitting iperf servers".format(run)
        for server in servers:
            net.hosts[server].sendInt()
            net.hosts[server].monitor()

    # for server, client in zip(server, client):
    #     # Start iperf on server host (non-blocking).
    #     serverCmd = "iperf -s &> /dev/null"
    #     net.hosts[server].sendCmd(serverCmd)

    #     results = []

    #     sleep(0.1)
    #     print "Testing server-client pair " + \
    #         str(net.hosts[server]) + " " + str(net.hosts[client])
    #     for each in range(0, runCount):
    #         clientCmd = "iperf -c" + net.hosts[server].IP() \
    #             + " -n " + payloadSize + " -y c -x CSMV"

    #         results.append(net.hosts[client].cmd(clientCmd))
    #         sleep(0.1)

    #     # Format the results into a json format
    #     entry = {'serverName': str(net.hosts[server]), 'serverIP': str(net.hosts[server].IP()),
    #              'clientName': str(net.hosts[client]), 'clientIP': str(net.hosts[client].IP()),
    #              'results': []}
    #     for each in results:
    #         entry['results'].append({'throughput': 0, 'fct': 0})
    #     entries.append(entry)

    #     net.hosts[server].sendInt()
    #     net.hosts[server].monitor()

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

