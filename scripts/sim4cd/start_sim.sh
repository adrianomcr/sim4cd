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

# SIM4CD_UNITY_BIN wins, otherwise look for the player export in or next to the repo
for candidate in "${SIM4CD_UNITY_BIN:-}" \
                 "${SIM4CD_UNITY_DIR:+${SIM4CD_UNITY_DIR}/sim4cdExample.x86_64}" \
                 "${repo_root}/unity/sim4cdExample.x86_64" \
                 "${repo_root}/../unity/sim4cdExample.x86_64"; do
    if [ -n "${candidate}" ] && [ -x "${candidate}" ]; then
        unity_bin=${candidate}
        break
    fi
done

# The Unity visualization is optional, so only warn when it is missing
if [ -z "${unity_bin:-}" ]; then
    echo "No Unity player found, skipping the Unity visualization." >&2
    echo "Set SIM4CD_UNITY_BIN to the sim4cdExample.x86_64 export to enable it." >&2
fi

# PX4 SITL runs in the foreground, so stop everything else once it exits
background_pids=()
cleanup() {
    for pid in "${background_pids[@]}"; do
        kill "${pid}" 2>/dev/null
    done
}
trap cleanup EXIT

echo "Running simulator with configuration file "$sim_config_file
python3 "${script_dir}/sim4cd_main.py" "${sim_config_file}" &
background_pids+=($!)

if [ -n "${unity_bin:-}" ]; then
    echo "Running the Unity visualization from ${unity_bin}"
    "${unity_bin}" &
    background_pids+=($!)
    python3 "${repo_root}/scripts/unity/update_unity_cam_pose.py" &
    background_pids+=($!)
fi

echo "Running PX4 SITL from ${px4_path}"
export PX4_SIM_MODEL=iris
cd ${px4_path}/build/px4_sitl_default
./bin/px4 -s etc/init.d-posix/rcS