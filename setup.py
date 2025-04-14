from setuptools import setup, find_packages

setup(
    name="sim4cd_project",
    version="0.0.1",
    packages=find_packages(where="scripts"),
    package_dir={"": "scripts"},
)

# On the location of the setup.py file, install with:
# pip3 install .
# or
# pip3 install -e .