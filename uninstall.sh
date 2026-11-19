#!/usr/bin/env bash
# Remove what install.sh added: the sim4cd launcher, its desktop entries, and PREFIX/share/sim4cd
# (Python environments, QGroundControl). The repository and system packages are kept; a PX4
# checkout cloned by install.sh and the GUI settings only go when asked for.
if [ -z "${BASH_VERSION:-}" ]; then echo 'Run this script with bash: ./uninstall.sh' >&2; exit 1; fi
set -euo pipefail
prefix="${HOME}/.local"
remove_px4=""
purge=0
assume_yes=0

usage() {
  cat <<'EOF'
Usage: ./uninstall.sh [options]

  --prefix PATH   Prefix that was given to install.sh (default: ~/.local)
  --remove-px4    Also delete the PX4 checkout that install.sh cloned
  --keep-px4      Keep that PX4 checkout without asking
  --purge         Also delete the GUI settings (~/.config/sim4cd)
  -y, --yes       Accept the default answer to every question (PX4 is kept)
  -h, --help      Show this help
EOF
}

while (($#)); do
  case "$1" in
    --prefix) prefix="${2:?Missing prefix}"; shift 2 ;;
    --remove-px4) remove_px4=1; shift ;;
    --keep-px4) remove_px4=0; shift ;;
    --purge) purge=1; shift ;;
    -y|--yes) assume_yes=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ "$prefix" = /* && "$prefix" != / ]] || { echo 'Use an absolute installation prefix other than /.' >&2; exit 2; }
prefix=$(realpath -m -- "$prefix")

data_dir="$prefix/share/sim4cd"
record="$data_dir/install.env"
apps_dir="$prefix/share/applications"
state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/sim4cd"
config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/sim4cd"

# Value of NAME in the record install.sh left, read in a clean shell.
record_value() {
  [[ -f $record ]] || return 0
  env -i "$BASH" -c '. "$1" >/dev/null 2>&1; printf "%s" "${!2:-}"' _ "$record" "$1" || true
}

px4_dir=$(record_value PX4_DIR)
if [[ -n $px4_dir && "$(record_value PX4_CLONED)" == 1 && -d $px4_dir ]]; then
  if [[ -z $remove_px4 ]]; then
    remove_px4=0
    if ((!assume_yes)) && [[ -t 0 ]]; then
      read -r -p "Delete the PX4 checkout that install.sh cloned in $px4_dir? [y/N] " reply || reply=""
      case "$reply" in [Yy]|[Yy][Ee][Ss]) remove_px4=1 ;; esac
    fi
  fi
elif [[ $remove_px4 == 1 ]]; then
  printf 'No PX4 checkout cloned by install.sh is recorded under %s, so none is deleted.\n' "$prefix"
  remove_px4=0
fi

rm -f -- "$prefix/bin/sim4cd" "$apps_dir/sim4cd.desktop" "$apps_dir/sim4cd-qgroundcontrol.desktop"
rm -rf -- "$data_dir" "$state_dir"
if command -v update-desktop-database >/dev/null && [[ -d $apps_dir ]]; then
  update-desktop-database "$apps_dir" || true
fi

if [[ $remove_px4 == 1 ]]; then
  # Only something that still looks like PX4, in case the directory was reused since.
  if [[ -f $px4_dir/Makefile && -d $px4_dir/platforms/posix ]]; then
    rm -rf -- "$px4_dir"
    printf 'Deleted PX4 in %s.\n' "$px4_dir"
  else
    printf '%s no longer looks like a PX4 checkout, so it was left alone.\n' "$px4_dir" >&2
  fi
elif [[ -n $px4_dir && -d $px4_dir ]]; then
  printf 'Kept PX4 in %s.\n' "$px4_dir"
fi

if ((purge)); then
  rm -rf -- "$config_dir"
  printf 'Deleted the GUI settings in %s.\n' "$config_dir"
elif [[ -d $config_dir ]]; then
  printf 'Kept the GUI settings in %s (--purge deletes them).\n' "$config_dir"
fi
printf 'Removed sim4cd from %s. The repository and the system packages were kept.\n' "$prefix"
