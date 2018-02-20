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


# Conventions
To recap, the following arguments will be used for launching tests.

--K [4,8,16]
--proto [tcp,mptcp]
--pmanager [fullmesh,ndiffports]
--ports [1-16]
--payloadsize [query,long,short]
--runcount [10]

Long messages are 100Mb, Query 10kb, short 500kb.

By default, tests will be run on mptcp-fullmesh with a runcount of 10 on k=4 with a payload size of 500kb.

## Middleware
logs/args.txt will contain arguments for tests. See above.