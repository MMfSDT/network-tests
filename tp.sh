#!/bin/bash

if [ $# -eq 0 ]; then
	echo "No arguments supplied."
	echo "$0 [server,<server-address>] [query/short/long]"
	exit 1

else
	if [ "$1" == "server" ]; then
		iperf -s -i 0.5 -y c
	else
		# parse data into simplified csv
		data=$(iperf -c $1 -t 5 -i 0.5 -y c -x CSMV)
		foo=$(echo "$data" | awk -F',' '{length(csv) == 0 ? csv = $9 : csv = csv "," $9} \
			END {print csv}')
			
		# determine mean, min, and max
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
