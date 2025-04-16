#!/usr/bin/env bash
script_dir=$(dirname "$0")
sim_config_file=$1


if [ -f /.dockerenv ]; then
    px4_path="/root/catkin_ws/src/PX4-Autopilot"
    # param_file="/root/catkin_ws/src/sim4cd/config/sim_params.json"
else
    px4_path=$(eval echo "~/catkin_ws/src/PX4")
    # param_file=$(eval echo "~/catkin_ws/src/sim4cd/config/sim_params.json")
fi

echo "Running simulator with configuration file "$sim_config_file
# python3 $script_dir/sim4cd_main.py $param_file &
python3 $script_dir/sim4cd_main.py $sim_config_file &

echo "Running PX4 SITL"
export PX4_SIM_MODEL=iris
cd ${px4_path}/build/px4_sitl_default
./bin/px4 -s etc/init.d-posix/rcS
