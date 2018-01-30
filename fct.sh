#!/bin/bash

if [ $# -eq 0 ]; then
	echo "No arguments supplied."
	echo "$0 [server,<server-address>] [query/short/long]"
	exit 1

else
	if [ "$1" == "server" ]; then
		python -m SimpleHTTPServer 8000
	else
		#time wget $1:8000/files/$2
		
	fi
fi
