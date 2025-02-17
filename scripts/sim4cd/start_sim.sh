#!/usr/bin/env bash

script_dir=$(dirname "$0")
#script_path=$(readlink -f "$0")
#echo $script_dir
source $script_dir/../../../devel/setup.bash

/root/catkin_ws/src/sim4cd/unity/sim4cdExample.x86_64 &

# sleep 1

roslaunch sim4cd sim4cd.launch parameters_path:=$1
