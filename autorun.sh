#!/bin/bash

cd ../mininet-topo-generator

# 1. Static-TCP vs. Static-MPTCP-Fullmesh vs.
## Static-MPTCP-ndiffports-K/2, for K = 4 varying, payloadsize (9 runs)

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --pmanager fullmesh --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --pmanager fullmesh --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --pmanager fullmesh --payloadsize long \
--post ../network-tests/postprocess.py --pcap


sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize long \
--post ../network-tests/postprocess.py --pcap


sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize long \
--post ../network-tests/postprocess.py --pcap


#2. ECMP-TCP vs. ECMP-MPTCP-Fullmesh vs. 
# ECMP-MPTCP-ndiffports-K/2, for K = 4, varying payloadsize (9 runs)

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize long \
--post ../network-tests/postprocess.py --pcap


sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize long \
--post ../network-tests/postprocess.py --pcap


sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize query \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize short \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize long \
--post ../network-tests/postprocess.py --pcap


# 3. ECMP-MPTCP-Fullmesh vs. 
# ECMP-MPTCP-ndiffports, for K = 4, long payloadsize, varying diffports [1, 2, 4, 6, 8] (6 runs)

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 1 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 4 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 6 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports -diffports 8 --payloadsize long \
--post ../network-tests/postprocess.py --pcap


#4. ECMP-MPTCP-Fullmesh vs.
# ECMP-MPTCP-ndiffports, for K = 8, long payloadsize, varying diffports [1, 2, 4, 6, 8] (6 runs)

sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize long \
--post ../network-tests/postprocess.py --pcap


sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager ndiffports -diffports 1 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager ndiffports -diffports 2 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager ndiffports -diffports 4 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager ndiffports -diffports 6 --payloadsize long \
--post ../network-tests/postprocess.py --pcap

sudo ./run.sh --test ../network-tests/test.py \
--K 8 --router ecmp --proto mptcp --pmanager ndiffports -diffports 8 --payloadsize long \
--post ../network-tests/postprocess.py --pcap