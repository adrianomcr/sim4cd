#!/usr/bin/env bash

script_dir=$(dirname "$0")
#script_path=$(readlink -f "$0")
#echo $script_dir
source $script_dir/../../../devel/setup.bash

roslaunch sim4cd sim4cd.launch parameters_path:=$1
