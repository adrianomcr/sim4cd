#!/usr/bin/env bash
script_dir=$(dirname "$0")


if [ -f /.dockerenv ]; then
    px4_path="/root/catkin_ws/src/PX4-Autopilot"
    param_file="/root/catkin_ws/src/sim4cd/config/sim_params.json"
else
    px4_path=$(eval echo "~/catkin_ws/src/PX4")
    param_file=$(eval echo "~/catkin_ws/src/sim4cd/config/sim_params.json")
fi

python3 $script_dir/sim4cd_main.py $param_file &

export PX4_SIM_MODEL=iris
cd ${px4_path}/build/px4_sitl_default
./bin/px4 -s etc/init.d-posix/rcS
