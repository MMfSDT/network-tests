#!/bin/bash

sudo killall nohup
sudo killall autorun.sh
sudo killall ../behavioral-model/targets/simple_router/.libs/lt-simple_router
sudo killall run.sh
sudo pkill -f topogen.py
sudo pkill -f postprocess.py
sudo killall iperf
