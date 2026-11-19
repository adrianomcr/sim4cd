#!/usr/bin/env bash
# Set up sim4cd for the invoking user: system packages, a Python environment, PX4 SITL and
# QGroundControl when wanted, and a `sim4cd` launcher plus desktop entry that know where PX4 is.
# Rerunning it is safe, and is the way to point sim4cd at another PX4 checkout.
if [ -z "${BASH_VERSION:-}" ]; then echo 'Run this script with bash: ./install.sh' >&2; exit 1; fi
set -Eeuo pipefail

sim4cd_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
prefix="${HOME}/.local"
px4_dir=""
px4_version="v1.13.3"
px4_mode=""   # use | build | skip, asked when empty
qgc_mode=""   # yes | no, asked when empty
install_deps=1
assume_yes=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Installs a `sim4cd` command and a desktop entry under PREFIX, with the Python environment
(and QGroundControl, if wanted) in PREFIX/share/sim4cd. Anything not set by an option is asked.

  --prefix PATH       Installation prefix (default: ~/.local)
  --px4-dir PATH      PX4-Autopilot checkout to use, or where to clone it
  --px4-version TAG   PX4 release to clone (default: v1.13.3)
  --build-px4         Clone PX4 if it is missing and build SITL, without asking
  --no-build-px4      Never clone or build PX4, only use one that is already built
  --qgc, --no-qgc     Download QGroundControl, or skip it, without asking
  --no-deps           Do not install system packages with apt
  -y, --yes           Accept the default answer to every question
  -h, --help          Show this help
EOF
}

while (($#)); do
  case "$1" in
    --prefix) prefix="${2:?Missing prefix}"; shift 2 ;;
    --px4-dir) px4_dir="${2:?Missing PX4 directory}"; shift 2 ;;
    --px4-version) px4_version="${2:?Missing PX4 version}"; shift 2 ;;
    --build-px4) px4_mode=build; shift ;;
    --no-build-px4) px4_mode=use; shift ;;
    --qgc) qgc_mode=yes; shift ;;
    --no-qgc) qgc_mode=no; shift ;;
    --no-deps) install_deps=0; shift ;;
    -y|--yes) assume_yes=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

step_name="starting"
tmp_files=()
trap 'printf "\ninstall.sh failed while %s (line %s).\n" "$step_name" "$LINENO" >&2' ERR
trap 'rm -f -- "${tmp_files[@]}"' EXIT

step() { step_name=${1,}; printf '\n==> %s\n' "$1"; }
section() { printf '\n%s\n' "$1"; }
note() { printf '  %s\n' "$*"; }
warn() { printf 'Warning: %s\n' "$*" >&2; }
die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

# confirm QUESTION DEFAULT: succeeds when the answer is yes. DEFAULT is y or n.
confirm() {
  local hint='[y/N]' reply
  [[ $2 == y ]] && hint='[Y/n]'
  if ((assume_yes)); then
    printf '  %s %s %s\n' "$1" "$hint" "$2"
    [[ $2 == y ]]
    return
  fi
  while :; do
    read -r -p "  $1 $hint " reply || reply=$2
    case "${reply:-$2}" in
      [Yy]|[Yy][Ee][Ss]) return 0 ;;
      [Nn]|[Nn][Oo]) return 1 ;;
    esac
  done
}

# ask_path PROMPT DEFAULT: sets $answer to the absolute path typed (DEFAULT is pre-filled),
# or to an empty string when nothing was given.
ask_path() {
  local reply=$2
  if ((assume_yes)); then
    printf '  %s: %s\n' "$1" "$2"
  else
    read -r -e -i "$2" -p "  $1: " reply || reply=$2
  fi
  if [[ $reply == "~" || $reply == "~/"* ]]; then reply=$HOME${reply:1}; fi
  answer=""
  if [[ -n $reply ]]; then answer=$(realpath -m -- "$reply"); fi
}

# write_file PATH MODE: replace PATH with standard input in one step.
write_file() {
  local tmp
  tmp=$(mktemp -- "$1.XXXXXX")
  cat >"$tmp"
  chmod "$2" -- "$tmp"
  mv -f -- "$tmp" "$1"
}

[[ "$prefix" = /* && "$prefix" != / ]] || die 'The prefix must be an absolute path other than /.'
prefix=$(realpath -m -- "$prefix")
case "$prefix" in
  *[\"\`\$\\%]*|*$'\n'*) die "Choose a prefix without any of these characters: \" \` \$ \\ %" ;;
esac
((EUID != 0)) || die 'Run install.sh as your own user, not with sudo. It asks for sudo itself, only to install system packages.'
[[ $px4_version =~ ^[A-Za-z0-9._/-]+$ ]] || die "Invalid PX4 version: $px4_version"
no_tty=0
if [[ ! -t 0 ]] && ((!assume_yes)); then assume_yes=1; no_tty=1; fi
# A sourced ROS workspace or similar would leak its packages into pip and into the PX4 build.
unset PYTHONHOME PYTHONPATH
export PIP_DISABLE_PIP_VERSION_CHECK=1

data_dir="$prefix/share/sim4cd"
venv="$data_dir/venv"
px4_venv="$data_dir/px4-venv"
record="$data_dir/install.env"
launcher="$prefix/bin/sim4cd"
apps_dir="$prefix/share/applications"
icon="$data_dir/sim4cd.png"
qgc_appimage="$data_dir/QGroundControl.AppImage"
qgc_desktop="$apps_dir/sim4cd-qgroundcontrol.desktop"

# Value of NAME in the record left by a previous install, read in a clean shell.
record_value() {
  [[ -f $record ]] || return 0
  env -i "$BASH" -c '. "$1" >/dev/null 2>&1; printf "%s" "${!2:-}"' _ "$record" "$1" || true
}

write_record() {
  mkdir -p -- "$data_dir"
  {
    printf '# Written by sim4cd install.sh, read back by it and by uninstall.sh.\n'
    printf 'SIM4CD_ROOT=%q\n' "$sim4cd_root"
    printf 'PX4_DIR=%q\n' "$px4_dir"
    printf 'PX4_CLONED=%q\n' "$px4_cloned"
  } | write_file "$record" 644
}

# The system interpreter rather than a conda or pyenv one that may come first on PATH,
# since that is the one the apt packages below are for.
find_python() {
  python=/usr/bin/python3
  [[ -x $python ]] || python=$(command -v python3 || true)
}

check_python() {
  [[ -n $python ]] || die 'python3 was not found.'
  "$python" -c 'import sys; sys.exit(sys.version_info < (3, 10))' \
    || die "sim4cd needs Python 3.10 or newer, found $("$python" -V 2>&1). Use the Docker setup in README.md on older systems."
}

python_version() { "$1" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || true; }

# make_venv DIR: create a virtualenv at DIR, unless a working one for this Python is there already.
make_venv() {
  if [[ -x $1/bin/python && "$(python_version "$1/bin/python")" == "$(python_version "$python")" ]] \
      && "$1/bin/python" -m pip --version >/dev/null 2>&1; then
    return 0
  fi
  rm -rf -- "$1"
  "$python" -m venv "$1"
  "$1/bin/python" -m pip install --upgrade pip
}

apt_installed() {
  [[ "$(dpkg-query -W -f='${Status}' "$1" 2>/dev/null || true)" == *"install ok installed"* ]]
}

# Each argument is a package, or "|"-separated alternatives for names that differ between
# Ubuntu releases (such as the 24.04 "t64" renames). Of a missing group, the first package
# apt knows about gets installed.
install_apt_packages() {
  local group package chosen missing=() selected=() alternatives=()
  for group in "$@"; do
    IFS='|' read -r -a alternatives <<<"$group"
    chosen=""
    for package in "${alternatives[@]}"; do
      if apt_installed "$package"; then chosen=$package; break; fi
    done
    [[ -n $chosen ]] || missing+=("$group")
  done
  if ((${#missing[@]} == 0)); then
    note 'All needed system packages are installed.'
    return 0
  fi

  note "Missing: ${missing[*]//|/ or }"
  command -v sudo >/dev/null || die 'sudo is needed to install system packages. Install them as root, or rerun with --no-deps.'
  sudo apt-get update || warn 'apt-get update reported errors; trying to install anyway.'
  for group in "${missing[@]}"; do
    IFS='|' read -r -a alternatives <<<"$group"
    chosen=${alternatives[-1]}
    for package in "${alternatives[@]}"; do
      if apt-cache show --no-all-versions "$package" >/dev/null 2>&1; then chosen=$package; break; fi
    done
    selected+=("$chosen")
  done
  sudo env DEBIAN_FRONTEND=noninteractive apt-get install -y "${selected[@]}"
}

px4_checkout() { [[ -f $1/Makefile && -d $1/platforms/posix ]]; }
# PX4 SITL writes its parameters and logs next to the binary, so the build must be writable too.
px4_ready() { [[ -x $1/build/px4_sitl_default/bin/px4 && -w $1/build/px4_sitl_default ]]; }
px4_describe() { git -C "$1" describe --tags --always 2>/dev/null || printf 'unknown version'; }

# Whether DIR can hold the PX4 to build: an existing checkout, or a place to clone one into.
px4_target_ok() {
  local parent=$1
  if [[ $1 == *[[:space:]]* ]]; then note "PX4 does not build in a path with spaces: $1"; return 1; fi
  if px4_checkout "$1"; then
    [[ -w $1 ]] || { note "$1 is not writable."; return 1; }
    return 0
  fi
  if [[ -e $1 && -n "$(ls -A -- "$1" 2>/dev/null)" ]]; then
    note "$1 exists and is not a PX4-Autopilot checkout."
    return 1
  fi
  while [[ ! -e $parent ]]; do parent=$(dirname -- "$parent"); done
  [[ -d $parent && -w $parent ]] || { note "Cannot create $1."; return 1; }
}

# Best guess for PX4: the previous choice, $PX4_DIR, or a checkout next to sim4cd, preferring
# one that is already built.
default_px4_dir() {
  local candidate parent
  parent=$(dirname -- "$sim4cd_root")
  local candidates=("$(record_value PX4_DIR)" "${PX4_DIR:-}" "$parent/PX4" "$parent/PX4-Autopilot" "$HOME/PX4-Autopilot")
  for candidate in "${candidates[@]}"; do
    if [[ -n $candidate ]] && px4_ready "$candidate"; then printf '%s' "$candidate"; return 0; fi
  done
  for candidate in "${candidates[@]}"; do
    if [[ -n $candidate ]] && px4_checkout "$candidate"; then printf '%s' "$candidate"; return 0; fi
  done
  printf '%s' "$parent/PX4"
}

# A QGroundControl the user already has, so that it is not downloaded twice.
find_qgc() {
  local candidate
  for candidate in "$(command -v QGroundControl || true)" "$(command -v qgroundcontrol || true)" \
      "$HOME"/Downloads/QGroundControl*.AppImage "$HOME"/Applications/QGroundControl*.AppImage \
      "$HOME"/QGroundControl*.AppImage /opt/QGroundControl*; do
    if [[ -e $candidate ]]; then printf '%s' "$candidate"; return 0; fi
  done
  grep -lis --exclude="${qgc_desktop##*/}" '^Exec=.*qgroundcontrol' \
    "$apps_dir"/*.desktop /usr/share/applications/*.desktop 2>/dev/null | head -n 1 || true
}

# version_ge A B: whether version A is B or newer.
version_ge() { [[ "$(printf '%s\n%s\n' "$1" "$2" | sort -V | head -n 1)" == "$2" ]]; }

# Newest glibc version (such as 2.38) that the QGroundControl binary in an AppImage links against,
# or nothing when it cannot be read. QGroundControl 4 keeps the binary at the top of the image.
qgc_needed_glibc() {
  local dir needed
  dir=$(mktemp -d)
  (cd "$dir" && { "$1" --appimage-extract usr/bin/QGroundControl; "$1" --appimage-extract QGroundControl; }) >/dev/null 2>&1 || true
  needed=$(cat -- "$dir/squashfs-root/usr/bin/QGroundControl" "$dir/squashfs-root/QGroundControl" 2>/dev/null \
    | grep -aoE 'GLIBC_2\.[0-9]+' | sort -uV | tail -n 1 || true)
  rm -rf -- "$dir"
  printf '%s' "${needed#GLIBC_}"
}

qgc_runs_here() {
  local needed
  needed=$(qgc_needed_glibc "$1")
  [[ -n $needed && -n $glibc ]] && version_ge "$glibc" "$needed"
}

# Copy the icon shipped in the QGroundControl AppImage next to it: an SVG from 5.1 on, a PNG before.
install_qgc_icon() {
  local dir icon
  dir=$(mktemp -d)
  (cd "$dir" && "$qgc_appimage" --appimage-extract 'usr/share/icons/hicolor/*/apps/QGroundControl.*') >/dev/null 2>&1 || true
  icon=$(find "$dir" -name QGroundControl.svg 2>/dev/null | head -n 1 || true)
  if [[ -z $icon ]]; then icon=$(find "$dir" -name QGroundControl.png 2>/dev/null | sort -V | tail -n 1 || true); fi
  if [[ -n $icon ]]; then cp -- "$icon" "$data_dir/QGroundControl.${icon##*.}"; fi
  rm -rf -- "$dir"
}

build_px4() {
  local dir=$1 sub requirements gcc_major flags_file
  if ((px4_cloned)); then
    step 'Fetching the PX4 submodules'
    # SITL does not use NuttX, and a shallow NuttX clone has no tags, which breaks PX4's version
    # header generation. A checkout cloned by someone else is left for the PX4 build to complete.
    for sub in platforms/nuttx/NuttX/nuttx platforms/nuttx/NuttX/apps; do
      if [[ ! -e $dir/$sub/.git ]]; then git -C "$dir" config "submodule.$sub.update" none; fi
    done
    git -C "$dir" submodule update --init --recursive --depth 1 --jobs 8
  fi

  step 'Installing the PX4 build dependencies'
  make_venv "$px4_venv"
  requirements=$(mktemp)
  tmp_files+=("$requirements")
  # pip 24+ rejects the "matplotlib>=3.0.*" specifier of PX4 v1.13, and empy 4 breaks its uORB
  # code generation.
  sed 's|matplotlib>=3\.0\.\*|matplotlib>=3.0|' "$dir/Tools/setup/requirements.txt" >"$requirements"
  "$px4_venv/bin/python" -m pip install -r "$requirements" 'empy==3.3.4'

  gcc_major=$(gcc -dumpversion 2>/dev/null || true)
  gcc_major=${gcc_major%%.*}
  [[ $gcc_major =~ ^[0-9]+$ ]] || gcc_major=0
  flags_file="$dir/cmake/px4_add_common_flags.cmake"
  # GCC 12+ reports a false -Warray-bounds positive in v1.13's src/lib/matrix, fatal with -Werror.
  if ((gcc_major >= 12)) && [[ -f $flags_file ]] && grep -Eq '^\s*-Werror$' "$flags_file"; then
    note "Turning -Werror off in $flags_file for GCC $gcc_major."
    sed -i 's|^\(\s*\)-Werror$|\1-Wno-error|' "$flags_file"
  fi

  step "Building PX4 SITL in $dir (this takes a while)"
  if ! (cd "$dir" && PATH="$px4_venv/bin:$PATH" VIRTUAL_ENV="$px4_venv" make px4_sitl_default); then
    die "The PX4 build failed. If $dir/build/px4_sitl_default is left from an older attempt or another toolchain, delete it and rerun install.sh."
  fi
  px4_ready "$dir" || die "The PX4 build did not produce $dir/build/px4_sitl_default/bin/px4."
}

printf 'sim4cd installer\n'
note "Repository: $sim4cd_root"
note "Prefix:     $prefix"
if ((no_tty)); then note 'Standard input is not a terminal, so the default answers are used.'; fi
os_id=$( (. /etc/os-release && printf '%s %s' "${ID:-}" "${VERSION_ID:-}") 2>/dev/null || true)
case "$os_id" in
  "ubuntu 22.04"|"ubuntu 24.04") ;;
  *) warn "install.sh is tested on Ubuntu 22.04 and 24.04, this is ${os_id:-an unknown system}." ;;
esac
find_python
if [[ -n $python ]]; then check_python; fi

section 'PX4 SITL'
if [[ -n $px4_dir ]]; then
  px4_dir=$(realpath -m -- "$px4_dir")
else
  px4_dir=$(realpath -m -- "$(default_px4_dir)")
fi
case "$px4_mode" in
  build) px4_target_ok "$px4_dir" || die "Cannot build PX4 in $px4_dir." ;;
  use)
    if ! px4_ready "$px4_dir"; then
      if px4_checkout "$px4_dir"; then
        warn "PX4 at $px4_dir is not built (or not writable), so simulations will not start until it is. Rerun with --build-px4 to build it."
      else
        warn "No PX4 checkout at $px4_dir, so sim4cd is set up without PX4."
        px4_mode=skip
        px4_dir=""
      fi
    fi
    ;;
esac

if [[ -z $px4_mode ]] && px4_ready "$px4_dir"; then
  note "Found PX4 SITL built at $px4_dir ($(px4_describe "$px4_dir"))."
  if confirm 'Use it?' y; then px4_mode=use; fi
fi
if [[ -z $px4_mode ]]; then
  if confirm "Clone and build PX4 $px4_version SITL? It downloads about 1 GB and takes 10 to 30 minutes." y; then
    px4_mode=build
    suggestion=$px4_dir
    if px4_ready "$suggestion"; then suggestion="$(dirname -- "$sim4cd_root")/PX4-$px4_version"; fi
    while :; do
      ask_path 'PX4 location' "$suggestion"
      if [[ -n $answer ]] && px4_target_ok "$answer"; then break; fi
      ((!assume_yes)) || die "Cannot clone PX4 into ${answer:-an empty path}. Use --px4-dir."
    done
    px4_dir=$answer
  else
    while :; do
      ask_path 'Existing PX4 checkout to use (leave empty to skip PX4)' ''
      if [[ -z $answer ]]; then
        px4_mode=skip
        px4_dir=""
        break
      elif px4_ready "$answer"; then
        px4_mode=use
        px4_dir=$answer
        break
      elif px4_checkout "$answer"; then
        if ! confirm "$answer has no usable SITL build. Build it now?" y; then
          px4_mode=use
          px4_dir=$answer
          break
        elif px4_target_ok "$answer"; then
          px4_mode=build
          px4_dir=$answer
          break
        fi
      else
        note "$answer is not a PX4-Autopilot checkout."
      fi
    done
  fi
fi
if [[ $px4_mode != build ]] && px4_checkout "${px4_dir:-/nonexistent}"; then
  px4_found_version=$(px4_describe "$px4_dir")
  if [[ $px4_found_version != "$px4_version"* ]]; then
    note "sim4cd is tested with PX4 $px4_version, $px4_dir is at $px4_found_version."
  fi
fi
case "$px4_mode" in
  build) note "PX4 SITL will be built in $px4_dir." ;;
  use) note "Using PX4 at $px4_dir." ;;
  skip) note 'Skipping PX4. Rerun install.sh to set it up later.' ;;
esac

section 'QGroundControl'
qgc_arch=$(uname -m)
glibc=$(getconf GNU_LIBC_VERSION 2>/dev/null || true)
glibc=${glibc##* }
# QGroundControl AppImages to try, newest first. Each release is built on a recent Ubuntu and needs
# its glibc: 5.1 and later need 2.38 (Ubuntu 24.04), and 5.0.8 is the last to run on 2.35 (22.04).
qgc_urls=()
if [[ -n $glibc ]] && version_ge "$glibc" 2.38 && [[ $qgc_arch == x86_64 || $qgc_arch == aarch64 ]]; then
  qgc_urls+=("https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl-$qgc_arch.AppImage")
fi
if [[ -n $glibc ]] && version_ge "$glibc" 2.35 && [[ $qgc_arch == x86_64 ]]; then
  qgc_urls+=("https://github.com/mavlink/qgroundcontrol/releases/download/v5.0.8/QGroundControl-x86_64.AppImage")
fi
qgc_ok=0
qgc_stale=0
if [[ -e $qgc_appimage ]]; then
  if qgc_runs_here "$qgc_appimage"; then
    qgc_ok=1
  else
    qgc_stale=1
    note "The QGroundControl in $qgc_appimage cannot run with this system's glibc ${glibc:-(unknown)}, so it will be replaced."
  fi
fi

if [[ $qgc_mode == no ]]; then
  note 'Skipping it.'
elif ((qgc_ok)); then
  note "Already installed in $qgc_appimage."
  qgc_mode=yes
elif ((${#qgc_urls[@]} == 0)); then
  [[ $qgc_mode != yes ]] || die "No QGroundControl AppImage runs on this system ($qgc_arch, glibc ${glibc:-unknown})."
  note "No QGroundControl AppImage runs on this system ($qgc_arch, glibc ${glibc:-unknown}), skipping it."
  qgc_mode=no
elif [[ $qgc_mode == yes ]]; then
  note 'It will be downloaded.'
else
  qgc_default=y
  other_qgc=$(find_qgc)
  if [[ -n $other_qgc ]]; then
    note "Found QGroundControl: $other_qgc"
    ((qgc_stale)) || qgc_default=n
  fi
  if confirm 'Download QGroundControl (about 200 MB) and add it to the applications menu?' "$qgc_default"; then
    qgc_mode=yes
  else
    qgc_mode=no
  fi
fi

if ((install_deps)); then
  step 'Installing system packages'
  command -v apt-get >/dev/null || die 'apt-get was not found. Install the packages listed in README.md, then rerun with --no-deps.'
  py_ver=""
  if [[ -n $python ]]; then py_ver=$(python_version "$python"); fi
  packages=(python3 "python3-venv${py_ver:+|python$py_ver-venv}" "python3-dev${py_ver:+|python$py_ver-dev}"
    python3-tk build-essential wmctrl
    libgl1 libglx-mesa0 libgl1-mesa-dri libegl1 'libglib2.0-0t64|libglib2.0-0' libxkbcommon-x11-0
    libxrender1 'libxt6t64|libxt6' libfontconfig1 libdbus-1-3 libxcb-xinerama0 libxcb-cursor0
    libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0)
  if [[ $px4_mode == build ]]; then
    packages+=(git rsync file zip unzip cmake ninja-build ccache libxml2-dev zlib1g-dev)
  fi
  if [[ $qgc_mode == yes ]]; then
    packages+=(curl ca-certificates 'libfuse2t64|libfuse2' libopengl0 gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl)
  fi
  install_apt_packages "${packages[@]}"
fi
find_python
check_python
"$python" -c 'import ensurepip, venv' 2>/dev/null || die 'Python venv support is missing. Install python3-venv.'

step 'Installing the sim4cd Python packages'
mkdir -p -- "$data_dir"
make_venv "$venv"
"$venv/bin/python" -m pip install -r "$sim4cd_root/requirements.txt"

step 'Checking the Python environment'
(cd "$sim4cd_root/scripts/qt_gui" && QT_QPA_PLATFORM=offscreen "$venv/bin/python" -c 'import qt_sim4cd') \
  || die 'The GUI modules failed to import, see the error above.'
(cd "$sim4cd_root/scripts/sim4cd" && "$venv/bin/python" -c 'import sim4cd_main') \
  || die 'The simulator modules failed to import, see the error above.'
qxcb=$("$venv/bin/python" -c 'import os, PyQt5; print(os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins", "platforms", "libqxcb.so"))')
missing_libs=""
if [[ -f $qxcb ]]; then
  missing_libs=$(ldd "$qxcb" 2>/dev/null | awk '/not found/ {print $1}' | sort -u | tr '\n' ' ' || true)
fi
if [[ -n $missing_libs ]]; then
  warn "Qt's X11 plugin cannot find $missing_libs. The GUI will not open until those libraries are installed."
else
  note 'The GUI and simulator modules import fine.'
fi

px4_cloned=0
if [[ -n $px4_dir && $px4_dir == "$(record_value PX4_DIR)" && "$(record_value PX4_CLONED)" == 1 ]]; then
  px4_cloned=1
fi
if [[ $px4_mode == build ]]; then
  if ! px4_checkout "$px4_dir"; then
    step "Cloning PX4 $px4_version into $px4_dir"
    mkdir -p -- "$px4_dir"
    git clone --depth 1 --branch "$px4_version" https://github.com/PX4/PX4-Autopilot.git "$px4_dir"
    px4_cloned=1
    write_record
  fi
  if px4_ready "$px4_dir"; then
    note "PX4 SITL is already built in $px4_dir."
  else
    build_px4 "$px4_dir"
  fi
fi

if ((qgc_stale)); then
  rm -f -- "$qgc_appimage" "$data_dir/QGroundControl.svg" "$data_dir/QGroundControl.png" "$qgc_desktop"
fi
if [[ $qgc_mode == yes && ! -x $qgc_appimage ]]; then
  step 'Downloading QGroundControl'
  tmp_files+=("$qgc_appimage.part")
  for url in "${qgc_urls[@]}"; do
    note "From $url"
    if ! curl -fL --retry 3 --progress-bar -o "$qgc_appimage.part" "$url"; then
      note 'The download failed.'
      continue
    fi
    chmod 755 -- "$qgc_appimage.part"
    if qgc_runs_here "$qgc_appimage.part"; then
      mv -f -- "$qgc_appimage.part" "$qgc_appimage"
      break
    fi
    note "That build needs glibc $(qgc_needed_glibc "$qgc_appimage.part"), newer than this system's $glibc."
  done
  [[ -x $qgc_appimage ]] || warn 'No QGroundControl download runs on this system, so it was not installed.'
fi

step 'Installing the launcher and desktop entries'
mkdir -p -- "$prefix/bin" "$apps_dir"
install -m 644 -- "$sim4cd_root/scripts/qt_gui/resources/icon.png" "$icon"
{
  printf '#!/usr/bin/env bash\n'
  printf '# Generated by the sim4cd install.sh; rerun it to change the paths below.\n'
  printf 'sim4cd_root=%q\n' "$sim4cd_root"
  printf 'sim4cd_venv=%q\n' "$venv"
  printf 'installed_px4_dir=%q\n' "$px4_dir"
  cat <<'EOF'
set -euo pipefail
log_file="${XDG_STATE_HOME:-$HOME/.local/state}/sim4cd/sim4cd.log"
logging=0

say() {
  printf 'sim4cd: %s\n' "$1" >&2
  if ((logging)) && command -v notify-send >/dev/null; then
    notify-send --app-name=sim4cd --icon="$2" sim4cd "$1" || true
  fi
}
fail() { say "$1" dialog-error; exit 1; }

# The desktop entry passes --log: without a terminal, the output has to go somewhere readable.
if [[ ${1:-} == --log ]]; then
  shift
  if mkdir -p -- "${log_file%/*}" 2>/dev/null; then
    exec >"$log_file" 2>&1
    logging=1
  fi
fi

gui="$sim4cd_root/scripts/qt_gui/qt_sim4cd.py"
[[ -f $gui ]] || fail "sim4cd is no longer in $sim4cd_root. Run install.sh again from where it is now."
[[ -x $sim4cd_venv/bin/python ]] || fail "The sim4cd Python environment is missing. Run $sim4cd_root/install.sh again."
if [[ -n $installed_px4_dir ]]; then
  export PX4_DIR=$installed_px4_dir
  [[ -x $PX4_DIR/build/px4_sitl_default/bin/px4 ]] \
    || say "No PX4 SITL build in $PX4_DIR, so simulations will not start. Run $sim4cd_root/install.sh again to set one up." dialog-warning
fi

export VIRTUAL_ENV=$sim4cd_venv
# start_sim.sh and the Unity bridge run plain python3, which has to be the venv one.
export PATH="$sim4cd_venv/bin:$PATH"
unset PYTHONHOME PYTHONPATH
# VTK draws through GLX, which only works with Qt's X11 (XWayland on Wayland) platform plugin.
export QT_QPA_PLATFORM=xcb
# Window instance name, which the desktop matches against StartupWMClass in sim4cd.desktop.
export RESOURCE_NAME=sim4cd

case "${1:-}" in
  -h|--help)
    printf 'Usage: sim4cd [--log] [--headless [PARAMS.json]]\n\n'
    printf 'Starts the sim4cd GUI. With --headless, runs the simulator and PX4 SITL in this\n'
    printf 'terminal instead, from PARAMS.json (default: %s).\n' "$sim4cd_root/config/sim_params.json"
    printf 'With --log, the output goes to %s and errors are\n' "$log_file"
    printf 'shown as desktop notifications; the applications menu entry starts sim4cd that way.\n\n'
    printf 'PX4:  %s\n' "${PX4_DIR:-not set}"
    exit 0
    ;;
  --headless)
    params=$(realpath -m -- "${2:-$sim4cd_root/config/sim_params.json}")
    [[ -f $params ]] || fail "No parameter file $params."
    exec "$sim4cd_root/scripts/sim4cd/start_sim.sh" "$params"
    ;;
esac

if ((logging)); then
  "$sim4cd_venv/bin/python" "$gui" "$@" || fail "sim4cd stopped with an error. The details are in $log_file."
  exit 0
fi
exec "$sim4cd_venv/bin/python" "$gui" "$@"
EOF
} | write_file "$launcher" 755

write_file "$apps_dir/sim4cd.desktop" 644 <<EOF
[Desktop Entry]
Type=Application
Name=Sim4CD
GenericName=Drone Simulator
Comment=Simulator for a custom drone, flown by PX4 SITL
Exec="$launcher" --log
Icon=$icon
Terminal=false
Categories=Science;Engineering;
Keywords=drone;quadcopter;multirotor;PX4;SITL;
StartupWMClass=sim4cd
EOF
desktop_entries=("$apps_dir/sim4cd.desktop")

if [[ -x $qgc_appimage ]]; then
  if [[ ! -f $data_dir/QGroundControl.svg && ! -f $data_dir/QGroundControl.png ]]; then install_qgc_icon; fi
  qgc_icon=QGroundControl
  if [[ -f $data_dir/QGroundControl.svg ]]; then
    qgc_icon=$data_dir/QGroundControl.svg
  elif [[ -f $data_dir/QGroundControl.png ]]; then
    qgc_icon=$data_dir/QGroundControl.png
  fi
  write_file "$qgc_desktop" 644 <<EOF
[Desktop Entry]
Type=Application
Name=QGroundControl
Comment=Ground control station, installed for sim4cd
Exec="$qgc_appimage"
Icon=$qgc_icon
Terminal=false
Categories=Utility;
StartupWMClass=QGroundControl
EOF
  desktop_entries+=("$qgc_desktop")
fi

if command -v desktop-file-validate >/dev/null; then
  for entry in "${desktop_entries[@]}"; do
    desktop-file-validate "$entry" || warn "$entry did not validate."
  done
fi
if command -v update-desktop-database >/dev/null; then update-desktop-database "$apps_dir" || true; fi
write_record

printf '\nsim4cd is installed.\n'
note "Start it from the applications menu (Sim4CD), or run: $launcher"
case "$px4_mode" in
  skip) note 'PX4:   not set up, so the simulator cannot start yet. Rerun install.sh to add it.' ;;
  *) note "PX4:   $px4_dir" ;;
esac
if [[ -x $qgc_appimage ]]; then note "QGroundControl: in the applications menu, or $qgc_appimage"; fi
if [[ -n $missing_libs ]]; then warn "The GUI needs these missing libraries: $missing_libs"; fi
case ":$PATH:" in
  *":$prefix/bin:"*) ;;
  *)
    if [[ $prefix == "$HOME/.local" ]]; then
      note "$prefix/bin is not on PATH yet. Ubuntu adds it at login, so log out and back in, or use the full path."
    else
      note "$prefix/bin is not on PATH. Add it there, or use the full path."
    fi
    ;;
esac
note 'Rerun ./install.sh to change PX4 or update the Python packages; ./uninstall.sh removes sim4cd.'
