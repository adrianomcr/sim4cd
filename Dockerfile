# Use the official ROS Noetic image based on Ubuntu 20.04
FROM ros:noetic-ros-base-focal

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive
# Set DISPLAY environment variable
ENV DISPLAY=:0
# Set runtime directory for qt applications
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
RUN mkdir -p /tmp/runtime-root && chmod 0700 /tmp/runtime-root

# Update and install necessary tools and system libraries for pip packages
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    cmake \
    python3-pip \
    python3-catkin-tools \
    ros-noetic-rviz \
    ros-noetic-tf2-ros \
    ros-noetic-rosbridge-suite \
    ros-noetic-dynamic-reconfigure \
    ros-noetic-mavros \
    wmctrl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libzmq3-dev \
    libvtk7-dev \
    python3-pil \
    python3-pil.imagetk \
    python3-tk \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip3 install \
    ttkthemes \
    magnetic_field_calculator \
    pymavlink \
    vtk \
    zmq \
    kconfiglib \
    packaging \
    jinja2 \
    jsonschema \
    toml \
    psutil \
    pyros-genmsg

# Clone PX4
WORKDIR /root/catkin_ws/src
RUN git clone --depth 1 --branch v1.13.3 https://github.com/PX4/PX4-Autopilot.git PX4-Autopilot
RUN git -C PX4-Autopilot submodule update --depth 1 --init --recursive

# Install geographiclib
RUN /opt/ros/noetic/lib/mavros/install_geographiclib_datasets.sh

# Build PX4
RUN ["/bin/bash", "-c", " \
    cd PX4-Autopilot && \
    make distclean && \
    DONT_RUN=1 make px4_sitl none_iris"]
    
# Source the environment when starting a container
RUN echo "source /root/catkin_ws/devel/setup.bash" >> ~/.bashrc

# Copy the repo to the docker image
COPY . /root/catkin_ws/src/sim4cd

# Build the ROS workspace
WORKDIR /root/catkin_ws/
RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin build"

# Set the entry point to start a bash session with ROS environment sourced
CMD ["/bin/bash", "-c", "source /opt/ros/noetic/setup.bash && source ~/.bashrc && bash"]

# Needed for running source
SHELL ["/bin/bash", "-c"]

# Reset DEBIAN_FRONTEND (optional but good practice)
ENV DEBIAN_FRONTEND=dialog