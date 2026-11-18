#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Unity player settings used by the GUI: which export to start, and whether to start it
# with the simulation. Kept apart from the vehicle parameter file because this is a local
# visualization choice, not something the dynamics need.

import os
import subprocess
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDialog, QDialogButtonBox, QFileDialog,
                             QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
                             QVBoxLayout)

# Bundled Linux export name. A user-built player can be called anything; this is only the
# fallback looked up next to the repository.
DEFAULT_UNITY_EXECUTABLE_NAME = "sim4cdExample.x86_64"

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))


def _as_bool(value, default=False):
    """Interpret a cached value as a boolean (QSettings stores these as strings)."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def guess_unity_executable():
    """
    Path of a Unity player sitting in the usual places next to this repository.

    Returns:
        (str): Absolute path of the first executable found, or None.
    """
    candidates = (
        os.path.join(_REPO_ROOT, "unity", DEFAULT_UNITY_EXECUTABLE_NAME),
        os.path.join(_REPO_ROOT, "..", "unity", DEFAULT_UNITY_EXECUTABLE_NAME),
    )
    for candidate in candidates:
        path = os.path.abspath(candidate)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return None


def is_unity_executable(path):
    """
    Tell whether 'path' looks like a file the OS can run.

    Parameters:
        path (str): Candidate Unity player.

    Returns:
        (bool): True if the file exists and has the execute bit.
    """
    return bool(path) and os.path.isfile(path) and os.access(path, os.X_OK)


def launch_unity_executable(path):
    """
    Start the Unity player so the user can check that the export runs.

    The working directory is the folder of the binary: Unity looks for the matching
    '*_Data' directory next to it.

    Parameters:
        path (str): Path of the player executable.

    Returns:
        (subprocess.Popen): The started process.

    Raises:
        ValueError: If the path is missing or not executable.
        OSError: If the OS refused to start it.
    """
    if not is_unity_executable(path):
        raise ValueError(f"Not an executable file:\n{path}")

    return subprocess.Popen(
        [path],
        cwd=os.path.dirname(os.path.abspath(path)),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


class UnitySettings(object):
    """
    Whether the Unity player should start with the simulation, and which export to use.

    'executable_path' is None when no player has been chosen yet. 'enabled' is independent
    of the path so a previously selected export can be left in place while Unity is turned
    off.
    """

    def __init__(self, executable_path=None, enabled=None, guess_if_missing=True):
        if executable_path:
            path = os.path.abspath(executable_path)
            if not os.path.isfile(path):
                path = None
        elif guess_if_missing:
            path = guess_unity_executable()
        else:
            path = None

        self.executable_path = path
        if enabled is None:
            self.enabled = bool(path)
        else:
            self.enabled = _as_bool(enabled)

    def copy(self):
        return UnitySettings(self.executable_path, self.enabled, guess_if_missing=False)

    def __eq__(self, other):
        if not isinstance(other, UnitySettings):
            return NotImplemented
        return self.executable_path == other.executable_path and self.enabled == other.enabled

    def __repr__(self):
        return f"UnitySettings(executable_path={self.executable_path!r}, enabled={self.enabled})"

    def to_dict(self):
        """These settings as plain values, for the GUI cache to store."""
        return {
            "executable_path": os.path.abspath(self.executable_path) if self.executable_path else "",
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(values):
        """
        Rebuild settings from what 'to_dict' produced.

        Parameters:
            values (dict): Mapping as returned by 'to_dict', possibly incomplete.

        Returns:
            (UnitySettings): The restored settings, with a guessed path on a blank cache.
        """
        if not values:
            return UnitySettings()

        path = None
        guess = True
        if "executable_path" in values:
            path = str(values.get("executable_path") or "").strip() or None
            guess = False

        enabled = values.get("enabled") if "enabled" in values else None
        return UnitySettings(path, enabled, guess_if_missing=guess)

    def simulation_environment(self, env=None):
        """
        Environment variables that tell start_sim.sh whether to launch Unity, and from where.

        Parameters:
            env (dict): Base environment; defaults to a copy of os.environ.

        Returns:
            (dict): Environment to pass to the simulator subprocess.
        """
        result = dict(env if env is not None else os.environ)
        if not self.enabled:
            result["SIM4CD_UNITY_ENABLE"] = "0"
            result.pop("SIM4CD_UNITY_BIN", None)
            return result

        result["SIM4CD_UNITY_ENABLE"] = "1"
        if self.executable_path:
            result["SIM4CD_UNITY_BIN"] = self.executable_path
        return result


class UnityDialog(QDialog):
    """
    Editor for the Unity player path and whether it starts with the simulation.

    Cancel restores the settings the dialog was opened with. Test launches the export
    immediately from the path currently shown, without waiting for OK.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unity")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._initial = settings.copy()
        self._settings = settings.copy()
        self._test_process = None

        self._build_ui()
        self._load_into_widgets()

    def _build_ui(self):
        self.enable_box = QCheckBox("Launch Unity when the simulation starts", self)

        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText("Path of the Unity player executable")
        browse_button = QPushButton("Browse...", self)
        browse_button.clicked.connect(self._on_browse)

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(browse_button)

        note = QLabel(
            "The Unity executable must have the camera properly configured so the "
            "simulator can drive its pose (the bundled CameraController). Otherwise the "
            "view will not follow the vehicle.",
            self)
        note.setWordWrap(True)
        note.setStyleSheet("color: #555555;")

        test_button = QPushButton("Test executable", self)
        test_button.clicked.connect(self._on_test)
        self.status_label = QLabel(self)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #555555;")

        test_row = QHBoxLayout()
        test_row.addWidget(test_button)
        test_row.addWidget(self.status_label, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.enable_box)
        layout.addWidget(QLabel("Unity executable:", self))
        layout.addLayout(path_row)
        layout.addWidget(note)
        layout.addLayout(test_row)
        layout.addWidget(buttons)
        self.resize(640, 240)

    def _load_into_widgets(self):
        self.enable_box.setChecked(self._settings.enabled)
        path = self._settings.executable_path or ""
        self.path_edit.setText(path)
        self.path_edit.setToolTip(path)
        self.path_edit.setCursorPosition(len(path))

    def _settings_from_widgets(self):
        path = self.path_edit.text().strip() or None
        return UnitySettings(path, self.enable_box.isChecked(), guess_if_missing=False)

    def _on_browse(self):
        start = self.path_edit.text().strip()
        if not start:
            guessed = guess_unity_executable()
            start = os.path.dirname(guessed) if guessed else ""
        elif os.path.isdir(start):
            pass
        else:
            start = os.path.dirname(start)

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Unity executable", start, "All Files (*)")
        if path:
            self.path_edit.setText(path)
            self.path_edit.setToolTip(path)
            self.path_edit.setCursorPosition(len(path))

    def _on_test(self):
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.critical(self, "Unity", "Choose a Unity executable first.")
            self.status_label.setText("No executable selected.")
            return

        if self._test_process is not None and self._test_process.poll() is None:
            self.status_label.setText("A test instance is already running.")
            return

        try:
            self._test_process = launch_unity_executable(path)
        except (ValueError, OSError) as error:
            QMessageBox.critical(self, "Unity", str(error))
            self.status_label.setText("Could not start the executable.")
            return

        self.status_label.setText(f"Started {os.path.basename(path)}.")

    def settings(self):
        """Settings last accepted, or the ones the dialog was opened with if it was cancelled."""
        return self._settings.copy()

    def accept(self):
        chosen = self._settings_from_widgets()
        if chosen.enabled and not is_unity_executable(chosen.executable_path):
            reply = QMessageBox.question(
                self,
                "Unity",
                "The selected file is missing or not executable. Save these settings anyway?",
                QMessageBox.Yes | QMessageBox.Cancel,
                QMessageBox.Cancel)
            if reply != QMessageBox.Yes:
                return
        self._settings = chosen
        super().accept()

    def reject(self):
        self._settings = self._initial.copy()
        super().reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = UnityDialog(UnitySettings())
    if dialog.exec_() == QDialog.Accepted:
        print("accepted:", dialog.settings())
    else:
        print("cancelled")
