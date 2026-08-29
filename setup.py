from setuptools import setup, find_packages

setup(
    name="sim4cd_project",
    version="0.0.1",
    package_dir={"": "scripts"},
    packages=find_packages("scripts"),
    package_data={
        "qt_gui": ["resources/*"],
        "qt_gui.tab_all_params": ["*.ui"],
        "qt_gui.tab_actuators": ["*.ui"],
        "qt_gui.tab_geolocation": ["*.ui"],
        "qt_gui.tab_home": ["*.ui"],
        "qt_gui.tab_vehicle": ["*.ui"],
    },
    entry_points={
        "console_scripts": [
            "sim4cd-gui=qt_gui.qt_sim4cd:main",
        ]
    },
)

# Install from this directory with:
# python3 -m pip install --user -e .
