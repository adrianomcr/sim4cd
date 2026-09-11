# sim4cd - Simulator for a Custom Drone

This package is a simulator tailored for quadcopters with fixed rotors. It offers configurable drone characteristics, allowing users to replicate their own platform. Currently, the simulator integrates seamlessly with PX4 firmware.


## Docker setup

Clone sim4cd
```bash
mkdir -p ~/simulation_ws/src
cd ~/simulation_ws/src
git clone https://github.com/adrianomcr/sim4cd.git
```

Build the image
```bash
docker compose -f docker-compose.yaml build
```

Give docker access to the X server
```bash
xhost +local:docker
```

Run the docker container
```bash
docker compose -f docker-compose.yaml run --rm sim4cd bash
```

Within the docker container, run the legacy Tk GUI
```bash
rosrun sim4cd sim_gui.py
```

The Docker image currently packages that Tk GUI, not the Qt GUI below.


## Native setup

Install PX4
```bash
cd ~/catkin_ws/src
git clone --depth 1 --branch v1.13.3 https://github.com/PX4/PX4-Autopilot.git PX4
git -C PX4 submodule update --depth 1 --init --recursive
cd PX4
make distclean

pip3 install kconfiglib
pip3 install --user packaging
pip3 install --user jinja2
pip3 install --user jsonschema
pip3 install --user toml
DONT_RUN=1 make px4_sitl none_iris
```

The Qt GUI starts PX4 from `~/catkin_ws/src/PX4` (`scripts/sim4cd/start_sim.sh`).

Install MAVROS
```bash
sudo apt install ros-noetic-mavros
roscd mavros/../../lib/mavros/
sudo ./install_geographiclib_datasets.sh
pip3 install pymavlink
```



Install QGroundControl
```bash
sudo usermod -a -G dialout $USER # Needs to log out and log in
sudo apt-get remove modemmanager -y
sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
sudo apt install libqt5gui5 -y
sudo apt install libfuse2 -y
```
Download the AppImage from https://docs.qgroundcontrol.com/master/en/qgc-user-guide/getting_started/download_and_install.html.
```bash
cd ~/Downloads
chmod +x ./QGroundControl.AppImage
```

## Clone repo and build

The Qt GUI lives on the `add-python-qt-gui` branch.

```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
git clone -b add-python-qt-gui https://github.com/adrianomcr/sim4cd.git
cd ~/catkin_ws
catkin build
```


## Qt GUI

The Qt GUI is the main way to load a vehicle config and start the simulator (`Start Simulator` runs `scripts/sim4cd/start_sim.sh`).

### System packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-dev \
  libgl1 libglib2.0-0 libxkbcommon-x11-0 \
  libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 \
  libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
  libxcb-render-util0 libxcb-shape0
```

On Ubuntu 24.04, install `python3.12-venv` if `python3-venv` is not available. You can skip `libglib2.0-0` if apt reports it was renamed to `libglib2.0-0t64`.

### Python dependencies (venv)

Ubuntu 24.04 blocks installing pip packages into the system Python. Use a virtualenv:

```bash
cd ~/catkin_ws/src/sim4cd   # or wherever you cloned the repo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`vtk` is pinned to 9.4.1 in `requirements.txt` (9.6+ rotates the home-tab skybox).

### Run

From `scripts/qt_gui`, with `scripts/` on `PYTHONPATH` so `sim4cd` imports resolve:

```bash
cd ~/catkin_ws/src/sim4cd/scripts/qt_gui
PYTHONPATH=.. python3 qt_sim4cd.py
```

Alternatively, from the repo root with the venv active:

```bash
pip install -e .
sim4cd-gui
```

PX4 SITL is expected at `~/catkin_ws/src/PX4` (see `scripts/sim4cd/start_sim.sh`). QGroundControl is used as the GCS.


## Legacy Tk GUI

The older Tk GUI is still in `scripts/gui/sim_gui.py`.

```bash
sudo apt-get install wmctrl
pip3 install ttkthemes magnetic_field_calculator
```

```bash
rosrun sim4cd sim_gui.py
```

GUI Home tab\
<img src=".media/home.png" alt="GUI Home tab" width="600">

GUI Configuration: geographic location and local magnetic field\
<img src=".media/config_geolocation.png" alt="GUI Config Geolocation tab" width="600">

GUI Configuration: sensors properties\
<img src=".media/config_sensors.png" alt="GUI Config Sensors tab" width="600">

GUI Configuration: actuators properties\
<img src=".media/config_actuators.png" alt="GUI Config Actuators tab" width="600">

GUI Configuration: battery and efficiency properties\
<img src=".media/config_power.png" alt="GUI Config Power tab" width="600">

GUI Configuration: full list of simulator parameters\
<img src=".media/config_full_parameter_set.png" alt="GUI Config Full list of parameters tab" width="600">
