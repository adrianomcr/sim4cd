# sim4cd - Simulator for a Custom Drone

This package is a simulator tailored for quadcopters with fixed rotors. It offers configurable drone characteristics, allowing users to replicate their own platform. Currently, the simulator integrates seamlessly with PX4 firmware.


## Docker setup

Install clone sim4cd
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

Within the docker container, run the gui
```bash
rosrun sim4cd sim_gui.py
```


## Native setup

Install PX4
```bash
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
git checkout v1.13.3
git submodule update --recursive
make distclean

pip3 install kconfiglib
pip3 install --user packaging
pip3 install --user jinja2
pip3 install --user jsonschema
pip3 install --user toml
make px4_sitl none_iris

```

Instal MavRos
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

```bash
mkdir -p ~/simulation_ws/src
cd ~/simulation_ws/src
git clone https://github.com/adrianomcr/sim4cd.git
catkin build
```


## GUI

The intent of the GUI is to provide an fast and easy way to configure the simulator with an specific drone model.

### Install depenndencies

```bash
sudo apt-get install wmctrl
```

```bash
pip3 install ttkthemes
pip3 install magnetic_field_calculator
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
