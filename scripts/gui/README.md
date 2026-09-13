# Legacy Tk GUI

This is the original GUI of sim4cd, written with tkinter. It has been superseded by the Qt GUI in
`scripts/qt_gui` (see the [main README](../../README.md)), but it still works and is kept for reference.

Both GUIs read and write the same JSON parameter file (`config/sim_params.json`), so a vehicle configured
with one can be opened with the other.

## Dependencies

```bash
sudo apt-get install wmctrl python3-tk
pip install ttkthemes magnetic_field_calculator
```

`ttkthemes` and `magnetic_field_calculator` are already in the repository's `requirements.txt`, so a
virtualenv set up for the Qt GUI covers this one too.

## Run

From `scripts/`:

```bash
python3 -m gui.sim_gui
```

The Docker image in the repository root also carries this GUI, so the same command works inside the
container (from `/root/sim4cd_ws/src/sim4cd/scripts`).

Each configuration editor can also be opened on its own window, which is useful when editing a single group
of parameters. Again from `scripts/`:

```bash
python3 -m gui.cfg_actuators
```

The same applies to `gui.cfg_geolocation`, `gui.cfg_sensors`, `gui.cfg_vehicle`, `gui.cfg_power` and
`gui.full_set_params`.

## Tabs

The GUI has a *Home* tab to load, save and run the simulation, and a *Configuration* tab that groups the
parameter editors: *Geolocation*, *Sensors*, *Vehicle*, *Actuators*, *Power* and *Full Parameter Set*. The
*Interaction* tab is a placeholder that was never implemented.

GUI Home tab  
![GUI Home tab](../../.media/home.png)

GUI Configuration: geographic location and local magnetic field  
![GUI Config Geolocation tab](../../.media/config_geolocation.png)

GUI Configuration: sensors properties  
![GUI Config Sensors tab](../../.media/config_sensors.png)

GUI Configuration: actuators properties  
![GUI Config Actuators tab](../../.media/config_actuators.png)

GUI Configuration: battery and efficiency properties  
![GUI Config Power tab](../../.media/config_power.png)

GUI Configuration: full list of simulator parameters  
![GUI Config Full list of parameters tab](../../.media/config_full_parameter_set.png)
