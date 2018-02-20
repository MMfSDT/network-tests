The goal of this exercise is to create a bash-based or python-based measurement of flow completion time and throughput in a network.

# Running test.py
The script can be run either at launch of the mininet-topo-generator or within the Mininet CLI itself. 

## Configuration
Place the network-tests and mininet-topo-generator repositories in one directory.

## Mininet-topo-generator
Go to the root directory of the mininet-topo-generator repository and run the following snippet.
```
sudo ./run_static.sh --test ../network-tests/test.py
````

## Within the mininet CLI
```
source ../network-tests/commands.txt
```

# Output
The test results will be placed into the logs/ directory with file name format <filesize>-<testcount>.txt. The results are in a CSV format as indicated below.
```
<server-name>,<host-name>,data
```
for example:
```
h000,h111,1231231
```