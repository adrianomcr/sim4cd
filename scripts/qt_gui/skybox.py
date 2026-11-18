#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Equirectangular skybox handling: the geometry that ties a pixel of the image to a
# direction in the scene, plus the user choices (image file, where north is, where the
# sun is) that are remembered between sessions.

import os
from math import asin, atan2, cos, degrees, hypot, pi, radians, sin

import numpy as np

# The scene frame is ENU: +X east, +Y north, +Z up.
#
# vtkSkybox with SetProjectionToSphere() samples the texture as
#
#     u = 0.5*atan2(d.right, d.front)/pi + 0.5
#     v = atan2(d.up, |(d.right, d.front)|)/pi + 0.5
#
# where "right" is FloorRight, "up" is the FloorPlane normal and "front" is up x right.
# The v axis grows towards the zenith whereas image rows are counted from the top, so
# the conversions below flip it.

DEFAULT_SKYBOX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "skybox.png")

# Markers of the bundled skybox. Its sun disk sits on pixel (4570, 687) of the
# 5760x2880 image, which is the sun the shadow direction used to be hard-coded from.
DEFAULT_NORTH_U = 0.5
DEFAULT_SUN_U = 4570.0 / 5760.0
DEFAULT_SUN_V = 687.0 / 2880.0

# The projected shadow runs away to infinity as the sun reaches the horizon; clamping the
# elevation keeps it at a usable distance.
MIN_SUN_ELEVATION_DEG = 3.0

# Sun markers are restricted to the sky, so their elevation is always positive.
MIN_PICKABLE_SUN_V = 0.5 - MIN_SUN_ELEVATION_DEG / 180.0


def north_u_to_floor_right_angle(north_u):
    """
    Angle of the skybox FloorRight axis that puts scene north at column 'north_u'.

    Parameters:
        north_u (float): Horizontal position of north in the image, 0 at the left edge, 1 at the right edge.

    Returns:
        (float): Angle of FloorRight measured counter-clockwise from +X (east), in radians.
    """
    return (north_u - 0.5) * 2.0 * pi


def floor_right_vector(north_u):
    """
    FloorRight vector to hand to vtkSkybox so that scene north lands on column 'north_u'.

    Parameters:
        north_u (float): Horizontal position of north in the image, in [0, 1].

    Returns:
        (tuple): The (x, y, z) FloorRight axis in scene coordinates.
    """
    angle = north_u_to_floor_right_angle(north_u)
    return (cos(angle), sin(angle), 0.0)


def uv_to_direction(u, v, north_u=DEFAULT_NORTH_U):
    """
    Convert an image pixel into the scene direction it is seen along.

    Parameters:
        u (float): Horizontal image position, 0 at the left edge, 1 at the right edge.
        v (float): Vertical image position, 0 at the top edge, 1 at the bottom edge.
        north_u (float): Horizontal position of north in the image, in [0, 1].

    Returns:
        (numpy.ndarray): Unit direction in scene coordinates (east, north, up).
    """
    theta = (u - 0.5) * 2.0 * pi
    elevation = (0.5 - v) * pi

    # Components along the texture frame axes (right, up, front) of the skybox shader.
    right = cos(elevation) * sin(theta)
    up = sin(elevation)
    front = cos(elevation) * cos(theta)

    angle = north_u_to_floor_right_angle(north_u)
    return np.array([
        right * cos(angle) - front * sin(angle),
        right * sin(angle) + front * cos(angle),
        up,
    ])


def direction_to_uv(direction, north_u=DEFAULT_NORTH_U):
    """
    Convert a scene direction into the image pixel that shows it.

    Parameters:
        direction (sequence): Direction in scene coordinates (east, north, up), not necessarily normalized.
        north_u (float): Horizontal position of north in the image, in [0, 1].

    Returns:
        (tuple): The (u, v) image position, both in [0, 1] and v counted from the top.
    """
    d = np.asarray(direction, dtype=float)
    angle = north_u_to_floor_right_angle(north_u)

    right = d[0] * cos(angle) + d[1] * sin(angle)
    front = -d[0] * sin(angle) + d[1] * cos(angle)
    up = d[2]

    u = (atan2(right, front) / (2.0 * pi) + 0.5) % 1.0
    v = 0.5 - atan2(up, hypot(right, front)) / pi
    return u, v


def direction_from_azimuth_elevation(azimuth_deg, elevation_deg):
    """
    Build a scene direction from a compass azimuth and an elevation.

    Parameters:
        azimuth_deg (float): Angle measured clockwise from north, in degrees.
        elevation_deg (float): Angle above the horizon, in degrees.

    Returns:
        (numpy.ndarray): Unit direction in scene coordinates (east, north, up).
    """
    az = radians(azimuth_deg)
    el = radians(elevation_deg)
    return np.array([cos(el) * sin(az), cos(el) * cos(az), sin(el)])


class SkyboxSettings(object):
    """
    Skybox image together with the north reference and the sun position picked on it.

    Positions are stored as normalized image coordinates so that they survive a resize
    of the image: 'u' runs left to right and 'v' runs top to bottom, both in [0, 1].
    """

    def __init__(self, path=None, north_u=DEFAULT_NORTH_U, sun_u=DEFAULT_SUN_U, sun_v=DEFAULT_SUN_V):
        self.path = path or DEFAULT_SKYBOX_PATH
        self.north_u = float(north_u) % 1.0
        self.sun_u = float(sun_u) % 1.0
        self.sun_v = min(max(float(sun_v), 0.0), MIN_PICKABLE_SUN_V)

    def copy(self):
        return SkyboxSettings(self.path, self.north_u, self.sun_u, self.sun_v)

    def __eq__(self, other):
        if not isinstance(other, SkyboxSettings):
            return NotImplemented
        return (os.path.abspath(self.path) == os.path.abspath(other.path)
                and abs(self.north_u - other.north_u) < 1e-9
                and abs(self.sun_u - other.sun_u) < 1e-9
                and abs(self.sun_v - other.sun_v) < 1e-9)

    def __repr__(self):
        return (f"SkyboxSettings(path={self.path!r}, north_u={self.north_u:.4f}, "
                f"sun_u={self.sun_u:.4f}, sun_v={self.sun_v:.4f})")

    def is_default_image(self):
        return os.path.abspath(self.path) == os.path.abspath(DEFAULT_SKYBOX_PATH)

    def floor_right(self):
        """FloorRight axis to hand to vtkSkybox, as an (x, y, z) tuple."""
        return floor_right_vector(self.north_u)

    def cardinal_u(self, quarter_turns):
        """
        Image column of a cardinal direction, used to annotate the image.

        Parameters:
            quarter_turns (int): 0 for north, 1 for east, 2 for south, 3 for west.

        Returns:
            (float): Horizontal image position of that direction, in [0, 1).
        """
        return (self.north_u + 0.25 * quarter_turns) % 1.0

    def sun_direction(self):
        """Unit vector pointing from the scene towards the sun, in scene coordinates."""
        return uv_to_direction(self.sun_u, self.sun_v, self.north_u)

    def sun_azimuth_deg(self):
        """Sun azimuth measured clockwise from north, in degrees."""
        d = self.sun_direction()
        return degrees(atan2(d[0], d[1])) % 360.0

    def sun_elevation_deg(self):
        """Sun elevation above the horizon, in degrees."""
        return degrees(asin(min(max(self.sun_direction()[2], -1.0), 1.0)))

    def shadow_azimuth_deg(self):
        """Azimuth the shadows are cast towards, measured clockwise from north, in degrees."""
        return (self.sun_azimuth_deg() + 180.0) % 360.0

    def shadow_offset(self, altitude):
        """
        Horizontal displacement between a point and the shadow it casts on the ground.

        Parameters:
            altitude (float): Height of the point above the ground plane, in meters.

        Returns:
            (tuple): The (dx, dy) offset to add to the point's position, in meters.
        """
        d = self.sun_direction()
        up = max(d[2], sin(radians(MIN_SUN_ELEVATION_DEG)))
        gamma = altitude / up
        return -gamma * d[0], -gamma * d[1]

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------
    def to_dict(self):
        """These settings as plain values, for the GUI cache to store."""
        return {
            "path": os.path.abspath(self.path),
            "north_u": self.north_u,
            "sun_u": self.sun_u,
            "sun_v": self.sun_v,
        }

    @staticmethod
    def from_dict(values):
        """
        Rebuild settings from what 'to_dict' produced.

        The marks only mean something on the image they were picked on, so an image that
        is missing or unreadable falls back to the bundled skybox and its own marks.

        Parameters:
            values (dict): Mapping as returned by 'to_dict', possibly incomplete.

        Returns:
            (SkyboxSettings): The restored settings.
        """
        path = values.get("path")
        if not path or not os.path.isfile(path):
            return SkyboxSettings()

        try:
            return SkyboxSettings(path,
                                  float(values.get("north_u", DEFAULT_NORTH_U)),
                                  float(values.get("sun_u", DEFAULT_SUN_U)),
                                  float(values.get("sun_v", DEFAULT_SUN_V)))
        except (TypeError, ValueError):
            return SkyboxSettings()


def is_vtk_readable(path):
    """
    Tell whether VTK has a reader for an image file, without decoding its pixels.

    Qt reads a few formats VTK does not, so the file dialog uses this to reject an image
    before it ends up half applied.

    Parameters:
        path (str): Path to the image.

    Returns:
        (bool): True if VTK recognizes the file.
    """
    import vtk

    if not os.path.isfile(path):
        return False
    return vtk.vtkImageReader2Factory().CreateImageReader2(path) is not None


def load_vtk_texture(path):
    """
    Build a VTK texture from an image file, guessing the format from its content.

    Parameters:
        path (str): Path to the equirectangular image.

    Returns:
        (tuple): The (reader, texture) pair. The reader has to be kept alive along with
                 the texture because it stays connected as its input.

    Raises:
        ValueError: If the file does not exist or no VTK reader handles its format.
    """
    import vtk

    if not os.path.isfile(path):
        raise ValueError(f"Image file not found:\n{path}")

    reader = vtk.vtkImageReader2Factory().CreateImageReader2(path)
    if reader is None:
        raise ValueError(f"Unsupported image format:\n{path}")

    reader.SetFileName(path)
    reader.Update()

    image = reader.GetOutput()
    if image is None or image.GetNumberOfPoints() == 0:
        raise ValueError(f"Could not read any pixel from:\n{path}")

    texture = vtk.vtkTexture()
    texture.SetInputConnection(reader.GetOutputPort())
    texture.InterpolateOn()
    return reader, texture
