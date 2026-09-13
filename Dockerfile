# This image provides Ubuntu with Python, the PX4 SITL build, and the Qt GUI.
FROM ubuntu:24.04

# Set environment variables for non-interactive installation
ENV DEBIAN_FRONTEND=noninteractive
# Set DISPLAY environment variable
ENV DISPLAY=:0
# Set runtime directory for qt applications
ENV XDG_RUNTIME_DIR=/tmp/runtime-root
RUN mkdir -p /tmp/runtime-root && chmod 0700 /tmp/runtime-root

# Toolchain for the PX4 SITL build, plus the X11/OpenGL libraries PyQt5 and VTK load at runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    rsync \
    file \
    zip \
    unzip \
    build-essential \
    cmake \
    ninja-build \
    ccache \
    gawk \
    genromfs \
    libtool \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    python3 \
    python3-dev \
    python3-venv \
    python3-tk \
    libgl1 \
    libglx-mesa0 \
    libgl1-mesa-dri \
    libegl1 \
    libglib2.0-0t64 \
    libxkbcommon-x11-0 \
    libxrender1 \
    libxt6 \
    libfontconfig1 \
    libdbus-1-3 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    wmctrl \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu 24.04 marks the system Python as externally managed (PEP 668), so everything Python
# goes into a virtualenv that is first on PATH, including for the PX4 build's code generation.
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}

# Clone PX4
ARG PX4_VERSION=v1.13.3
WORKDIR /root/sim4cd_ws/src
RUN git clone --depth 1 --branch ${PX4_VERSION} https://github.com/PX4/PX4-Autopilot.git PX4

# SITL does not build the NuttX platform, and a shallow clone of that submodule carries no tags,
# which makes PX4's git version header generation fail. Leave it out.
RUN git -C PX4 config submodule."platforms/nuttx/NuttX/nuttx".update none \
    && git -C PX4 config submodule."platforms/nuttx/NuttX/apps".update none \
    && git -C PX4 submodule update --depth 1 --init --recursive

WORKDIR /root/sim4cd_ws/src/PX4

# v1.13.3 predates this toolchain on three points: pip 24+ rejects the "matplotlib>=3.0.*"
# specifier, empy 4.x breaks the uORB code generation, and GCC 13 reports a false positive
# -Warray-bounds in src/lib/matrix that -Werror turns into a build failure.
RUN sed -i 's|matplotlib>=3.0\.\*|matplotlib>=3.0|' Tools/setup/requirements.txt \
    && sed -i 's|^\(\s*\)-Werror$|\1-Wno-error|' cmake/px4_add_common_flags.cmake \
    && pip install --no-cache-dir -r Tools/setup/requirements.txt \
    && pip install --no-cache-dir 'empy==3.3.4'

# Build SITL
RUN DONT_RUN=1 make px4_sitl none_iris

# Install the Python dependencies before the sources, so editing the repo does not redo this layer
WORKDIR /root/sim4cd_ws/src/sim4cd
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the repo to the docker image
COPY . .
RUN pip install --no-cache-dir -e .

# Where scripts/sim4cd/start_sim.sh looks for the PX4 binary
ENV PX4_DIR=/root/sim4cd_ws/src/PX4

# Start the Qt GUI
CMD ["sim4cd-gui"]

# Reset DEBIAN_FRONTEND (optional but good practice)
ENV DEBIAN_FRONTEND=dialog
