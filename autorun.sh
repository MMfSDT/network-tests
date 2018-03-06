#!/bin/bash
# run with `nohup sudo ./autorun.sh &`


cd ../mininet-topo-generator

update_status () {
	curl -d '{"message": "'"$1"'"}' -H "Content-Type: application/json" -X POST https://bash-status-update-bcfojakuzq.now.sh/
}

# New tests (March 6)

## STATIC - TCP
# test 1
update_status "1. static - tcp - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --payloadsize query --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "1. static - tcp - query - k = 4 - 5 runs (DONE)"

# test 2
update_status "2. static - tcp - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "2. static - tcp - short - k = 4 - 5 runs (DONE)"

# test 3
update_status "3. static - tcp - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router static --proto tcp --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "3. static - tcp - long - k = 4 - 5 runs (DONE)"

## ECMP - MPTCP - FULLMESH
# test 4
update_status "4. ecmp - mptcp - fullmesh - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize query --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "4. ecmp - mptcp - query - k = 4 - 5 runs (DONE)"

# test 5
update_status "5. ecmp - mptcp - fullmesh - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "5. ecmp - mptcp - short - k = 4 - 5 runs (DONE)"

# test 6
update_status "6. ecmp - mptcp - fullmesh - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "6. ecmp - mptcp - long - k = 4 - 5 runs (DONE)"

## ECMP - MPTCP - NDIFFPORTS - 4
# test 7
update_status "7. ecmp - mptcp - 2 ndiffports - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize query --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "7. ecmp - mptcp - 2 ndiffports - query - k = 4 - 5 runs (DONE)"

# test 8
update_status "8. ecmp - mptcp - 2 ndiffports - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "8. ecmp - mptcp - 2 ndiffports - short - k = 4 - 5 runs (DONE)"

# test 9
update_status "9. ecmp - mptcp - 2 ndiffports - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "9. ecmp - mptcp - 2 ndiffports - long - k = 4 - 5 runs (DONE)"

## PS - TCP
# test 10
update_status "10. ps - tcp - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto tcp --payloadsize query \
--post ../network-tests/postprocess.py --pcap

update_status "10. ps - tcp - query - k = 4 - 5 runs (DONE)"

# test 11
update_status "11. ps - tcp - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto tcp --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "11. ps - tcp - short - k = 4 - 5 runs (DONE)"

# test 12
update_status "12. ps - tcp - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto tcp --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "12. ps - tcp - long - k = 4 - 5 runs (DONE)"

## PS - MPTCP - FULLMESH
# test 13
update_status "13. ps - mptcp - fullmesh - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager fullmesh --payloadsize query --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "13. ps - mptcp - query - k = 4 - 5 runs (DONE)"

# test 14
update_status "14. ps - mptcp - fullmesh - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager fullmesh --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "14. ps - mptcp - short - k = 4 - 5 runs (DONE)"

# test 15
update_status "15. ps - mptcp - fullmesh - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager fullmesh --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "15. ps - mptcp - long - k = 4 - 5 runs (DONE)"

## PS - MPTCP - NDIFFPORTS - 4
# test 7
update_status "7. ps - mptcp - 4 ndiffports - query - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize query --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "7. ps - mptcp - 4 ndiffports - query - k = 4 - 5 runs (DONE)"

# test 2
update_status "2. ps - mptcp - 4 ndiffports - short - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize short --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "2. ps - mptcp - 4 ndiffports - short - k = 4 - 5 runs (DONE)"

# test 3
update_status "3. ps - mptcp - 4 ndiffports - long - k = 4 - 5 runs (RUNNING)"

sudo ./run.sh --test ../network-tests/test.py \
--K 4 --router ps --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize long --runcount 5 \
--post ../network-tests/postprocess.py --pcap

update_status "3. ps - mptcp - 4 ndiffports - long - k = 4 - 5 runs (DONE)"

# Old tests (pre-March 6)

# 1. Static-TCP vs. Static-MPTCP-Fullmesh vs.
## Static-MPTCP-ndiffports-K/2, for K = 4 varying, payloadsize (9 runs)

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto tcp --pmanager fullmesh --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto tcp --pmanager fullmesh --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto tcp --pmanager fullmesh --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager fullmesh --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router static --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


#2. ECMP-TCP vs. ECMP-MPTCP-Fullmesh vs. 
# # ECMP-MPTCP-ndiffports-K/2, for K = 4, varying payloadsize (9 runs)

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto tcp --pmanager fullmesh --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize query \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize long \
# --post ../network-tests/postprocess.py --pcap


# 3. ECMP-MPTCP-Fullmesh vs. 
# ECMP-MPTCP-ndiffports, for K = 4, short payloadsize, varying diffports [1, 2, 4, 6, 8] (6 runs)

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 1 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 6 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 4 --router ecmp --proto mptcp --pmanager ndiffports --diffports 8 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap


#4. ECMP-MPTCP-Fullmesh vs.
# ECMP-MPTCP-ndiffports, for K = 8, short payloadsize, varying diffports [1, 2, 4, 6, 8] (6 runs)

# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager fullmesh --payloadsize short \
# --post ../network-tests/postprocess.py --pcap


# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager ndiffports --diffports 1 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager ndiffports --diffports 2 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager ndiffports --diffports 4 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager ndiffports --diffports 6 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap

# sudo ./run.sh --test ../network-tests/test.py \
# --K 8 --router ecmp --proto mptcp --pmanager ndiffports --diffports 8 --payloadsize short \
# --post ../network-tests/postprocess.py --pcap