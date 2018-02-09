#!/bin/bash

## 	Flow Completion Test Script
##	- Kyle Gomez
#
# 	Serves both server and client capabilities, saves outputs to a local file.
#	Arguments: <'server' | server-address> <query | short | long>

if [ $# -eq 0 ]; then
	echo "No arguments supplied."
	echo "$0 <'server' | server-address> <query | short | long>"
	exit 1

else
	if [ "$1" == "server" ]; then
		# The server runs an HTTP server in Python, with port 8000.
		# 	To make things simpler, three test files (to simulate flows) are available, with the following names and file sizes.
		#		| query: 10 kB
		#		| short: 500 kB
		#		| long: 1 MB
		python -m SimpleHTTPServer 8000
	else
		#time wget $1:8000/files/$2
		
	fi
fi
