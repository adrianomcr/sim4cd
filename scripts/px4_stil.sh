#!/usr/bin/env bash

export PX4_SIM_MODEL=iris

px4_path="$1"
cd ${px4_path}/build/px4_sitl_default
./bin/px4 -s etc/init.d-posix/rcS
