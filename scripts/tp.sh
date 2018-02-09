#!/bin/bash

## 	Througput Test Script
##	- Kyle Gomez
#
# 	Serves both server and client capabilities, saves outputs to a local file.
#	Arguments: <'server' | server-address>
#
#		SUGGESTED IMPROVEMENTS (Charles):
#			Periodic reports (-i) are a little bit useless, I think a much simpler route is to get the mean throughput ($9) within (-t) seconds.
#				This way, we can replicate the test over many hosts, *then* compute the mean, max, and min.
#			When integrating this with Python, however, I would suggest silencing the outputs of the commands, 
#				so as to use stdout to send data to Python. This will allow for easier creation of tests in the long run.

if [ $# -eq 0 ]; then
	echo "No arguments supplied."
	echo "$0 <server | server_address>"
	exit 1

else
	if [ "$1" == "server" ]; then
		# If script is called with the string "server", run the iperf server.
		# 	iperf will now run in (-s)erver mode, and will report in 0.5 second (-i)ntervals.
		# Note that if you're visually debugging the server, it's best to remove the CSV formatting argument (-y c).
		iperf -s -i 0.5 -y c
	else
		# If the script is called with an IP address however, run the iperf client.
		# 	iperf will run in (-c)lient mode connecting to $1, for an entire (-t)ime period of 5 seconds, while reporting in 0.5 second (-i)ntervals.
		# 	iperf will (-y)ield the output as CSV, and will e(-x)clude (C)onnection (S)ettings, (M)ulticast, and ser(V)er reports.
		# The output will be stored in the variable data.
		data=$(iperf -c $1 -t 5 -i 0.5 -y c -x CSMV)
		# The output is comma-separated: timestamp, client IP, client port, server IP, server port, ?, interval period, data transferred (bytes), bandwidth (bits)
		# 	Note that, to become human readable, you probably would want to convert the data transferred from bytes to Mebibytes, and the bandwidth from bits to Gigabits
		# Also, note that the last line of the output already prints the summary of the entire interval. Since the periodic reporting isn't really necessary,
		# 	we can make do wtihout the (-i) argument.

		# This just reads each line, grabs the bandwidth ($9), and outputs it into variable foo.
		foo=$(echo "$data" | awk -F',' '{length(csv) == 0 ? csv = $9 : csv = csv "," $9} \
			END {print csv}')
			
		# To determine min and max, we parse foo into an array, and manually check each element for min, max.
		IFS=',' read -r -a array <<< "$foo"
		min=$((9999999999))
		max=$((0))
		for element in "${array[@]}"; do
			total=$((total + $element));
			if ((element > max)); then 
				max=$element
			fi
			if ((element < min)); then 
				min=$element
			fi
		done
		# To get the mean, we divide the total with the array length.
		array_length=${#array[@]}
		mean=$(echo $total/$array_length | bc -l)

		# display results
		echo "Mean: " $mean
		echo "Max: " $max
		echo "Min: " $min
		echo "Data: " $foo

		# place data into output log TODO: variable output file
		echo $mean "," $max "," $min "," $foo | sed "s/[[:blank:]]//g" >> logs/tp.out
	fi
fi
