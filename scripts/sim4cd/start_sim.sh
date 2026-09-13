#!/usr/bin/env bash
script_dir=$(cd "$(dirname "$0")" && pwd)
repo_root=$(cd "${script_dir}/../.." && pwd)
sim_config_file=$1

# PX4_DIR wins, otherwise look for a PX4 checkout next to the repo
for candidate in "${PX4_DIR:-}" "${repo_root}/../PX4" "${repo_root}/../PX4-Autopilot"; do
    if [ -n "${candidate}" ] && [ -x "${candidate}/build/px4_sitl_default/bin/px4" ]; then
        px4_path=$(cd "${candidate}" && pwd)
        break
    fi
done

if [ -z "${px4_path:-}" ]; then
    echo "No built PX4 SITL found. Set PX4_DIR to your PX4 checkout." >&2
    exit 1
fi

echo "Running simulator with configuration file "$sim_config_file
python3 $script_dir/sim4cd_main.py $sim_config_file &

echo "Running PX4 SITL from ${px4_path}"
export PX4_SIM_MODEL=iris
cd ${px4_path}/build/px4_sitl_default
./bin/px4 -s etc/init.d-posix/rcS
