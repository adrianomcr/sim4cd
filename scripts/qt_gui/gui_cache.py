#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Cache of the GUI's own state, so that a session starts where the previous one left off.
#
# This is deliberately kept apart from the simulation parameter file: nothing stored here
# is needed to run a simulation, it only saves the user from setting the GUI up again.
# Anything cached is treated as a hint, never as a requirement, so a stale or hand-edited
# cache degrades to the defaults instead of breaking the startup.

import os

from PyQt5.QtCore import QSettings

import skybox as SB
import unity_settings as US

_ORGANIZATION = "sim4cd"
_APPLICATION = "gui"

_SKYBOX_GROUP = "skybox"
_UNITY_GROUP = "unity"
_CONFIG_FILE_KEY = "config_file_path"


def _open_storage():
    """QSettings backing the cache (an INI-style file under the user's config directory)."""
    return QSettings(_ORGANIZATION, _APPLICATION)


def storage_path():
    """Path of the file the cache is kept in, useful when reporting what was restored."""
    return _open_storage().fileName()


class GuiCache(object):
    """
    GUI state remembered between sessions.

    Attributes:
        config_file_path (str): Simulation parameter file that was open last, or None.
        skybox (skybox.SkyboxSettings): Skybox image with the east/north reference and the
                                        sun position marked on it.
        unity (unity_settings.UnitySettings): Unity player path and whether to launch it
                                              with the simulation.
    """

    def __init__(self, config_file_path=None, skybox=None, unity=None):
        self.config_file_path = os.path.abspath(config_file_path) if config_file_path else None
        self.skybox = skybox.copy() if skybox is not None else SB.SkyboxSettings()
        self.unity = unity.copy() if unity is not None else US.UnitySettings()

    def copy(self):
        return GuiCache(self.config_file_path, self.skybox, self.unity)

    def __eq__(self, other):
        if not isinstance(other, GuiCache):
            return NotImplemented
        return (self.config_file_path == other.config_file_path
                and self.skybox == other.skybox
                and self.unity == other.unity)

    def __repr__(self):
        return (f"GuiCache(config_file_path={self.config_file_path!r}, "
                f"skybox={self.skybox!r}, unity={self.unity!r})")

    @staticmethod
    def load(storage=None):
        """
        Read back what the previous session cached.

        Parameters:
            storage (QSettings): Optional backing store. Tests pass a throwaway INI file;
                                 the GUI uses the per-user file under the sim4cd config dir.

        Returns:
            (GuiCache): The restored state, with defaults wherever nothing usable was cached.
        """
        storage = storage or _open_storage()

        config_file_path = storage.value(_CONFIG_FILE_KEY, type=str) or None
        if config_file_path and not os.path.isfile(config_file_path):
            config_file_path = None

        storage.beginGroup(_SKYBOX_GROUP)
        skybox_values = {key: storage.value(key) for key in storage.childKeys()}
        storage.endGroup()

        storage.beginGroup(_UNITY_GROUP)
        unity_values = {key: storage.value(key) for key in storage.childKeys()}
        storage.endGroup()

        return GuiCache(config_file_path,
                        SB.SkyboxSettings.from_dict(skybox_values),
                        US.UnitySettings.from_dict(unity_values))

    def save(self, storage=None):
        """Write the current state back, to be picked up by the next session."""
        storage = storage or _open_storage()

        if self.config_file_path:
            storage.setValue(_CONFIG_FILE_KEY, os.path.abspath(self.config_file_path))
        else:
            storage.remove(_CONFIG_FILE_KEY)

        storage.beginGroup(_SKYBOX_GROUP)
        storage.remove("")
        for key, value in self.skybox.to_dict().items():
            storage.setValue(key, value)
        storage.endGroup()

        storage.beginGroup(_UNITY_GROUP)
        storage.remove("")
        for key, value in self.unity.to_dict().items():
            storage.setValue(key, value)
        storage.endGroup()

        storage.sync()
