#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# Dialog that lets the user pick the skybox image and mark, directly on it, where north
# is and where the sun is. Those two marks are what orients the scene and aims the
# shadows, so the dialog draws them back on the image together with the values they
# produce.

import os
import sys

from PyQt5.QtCore import QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QFileDialog, QFrame,
                             QGroupBox, QHBoxLayout, QLabel, QMessageBox, QPushButton,
                             QRadioButton, QSizePolicy, QVBoxLayout, QWidget)

import skybox as SB

# Largest image the dialog keeps around for display; equirectangular skyboxes are often
# several thousand pixels wide and scaling once up front keeps repainting cheap.
MAX_PREVIEW_WIDTH = 1600

# Sky/ground grid used to look for the brightest spot when guessing the sun.
SUN_GUESS_GRID_WIDTH = 64

IMAGE_FILTER = ("Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.hdr *.pnm *.ppm);;"
                "PNG (*.png);;JPEG (*.jpg *.jpeg);;All Files (*)")

_NORTH_COLOR = QColor(80, 220, 255)
_CARDINAL_COLOR = QColor(200, 200, 200)
_SUN_COLOR = QColor(255, 210, 60)
_SHADOW_COLOR = QColor(255, 130, 130)
_HORIZON_COLOR = QColor(255, 255, 255, 140)

_CARDINAL_NAMES = ("N", "E", "S", "W")


def guess_sun_uv(image, grid_width=SUN_GUESS_GRID_WIDTH):
    """
    Look for the brightest spot of the sky, as a first guess of where the sun is.

    Averaging the image down to a coarse grid blurs away small bright details such as
    cloud edges, so a broad sun glow wins over them.

    Parameters:
        image (QImage): Equirectangular image to inspect.
        grid_width (int): Number of columns of the coarse grid.

    Returns:
        (tuple): The (u, v) guess in normalized image coordinates, v counted from the top.
    """
    if image.isNull():
        return 0.5, 0.25

    grid_height = max(2, grid_width // 2)
    # Two steps, because scaling down by a very large factor in one go can skip over
    # whole regions of the source image instead of averaging them.
    coarse = image.convertToFormat(QImage.Format_RGB32)
    if coarse.width() > 8 * grid_width:
        coarse = coarse.scaled(8 * grid_width, 8 * grid_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    coarse = coarse.scaled(grid_width, grid_height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    best_luminance = -1.0
    best_uv = (0.5, 0.25)
    for y in range(grid_height // 2):
        for x in range(grid_width):
            color = coarse.pixelColor(x, y)
            luminance = 0.2126 * color.red() + 0.7152 * color.green() + 0.0722 * color.blue()
            if luminance > best_luminance:
                best_luminance = luminance
                best_uv = ((x + 0.5) / grid_width, (y + 0.5) / grid_height)
    return best_uv


class SkyboxImageCanvas(QWidget):
    """
    Shows the equirectangular image and lets the user click a position on it.

    Emits 'picked' with the normalized (u, v) coordinates of every click and drag, and
    draws the current north and sun marks on top of the image.
    """

    picked = pyqtSignal(float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = QPixmap()
        self._settings = None
        self.setMinimumSize(520, 260)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.CrossCursor)
        self.setAutoFillBackground(False)

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap if pixmap is not None else QPixmap()
        self.update()

    def set_settings(self, settings):
        self._settings = settings
        self.update()

    # -------------------------------------------------------------------------
    # Coordinate conversions
    # -------------------------------------------------------------------------
    def image_rect(self):
        """Area the image occupies inside the widget, keeping its aspect ratio."""
        if self._pixmap.isNull():
            return QRect(0, 0, self.width(), self.height())

        available = self.rect()
        scaled = self._pixmap.size().scaled(available.size(), Qt.KeepAspectRatio)
        return QRect(available.x() + (available.width() - scaled.width()) // 2,
                     available.y() + (available.height() - scaled.height()) // 2,
                     scaled.width(), scaled.height())

    def _uv_at(self, pos):
        rect = self.image_rect()
        if rect.width() <= 0 or rect.height() <= 0:
            return None
        u = (pos.x() - rect.x()) / float(rect.width())
        v = (pos.y() - rect.y()) / float(rect.height())
        return min(max(u, 0.0), 1.0), min(max(v, 0.0), 1.0)

    def _point_at(self, u, v):
        rect = self.image_rect()
        return QPoint(int(round(rect.x() + u * rect.width())),
                      int(round(rect.y() + v * rect.height())))

    # -------------------------------------------------------------------------
    # Interaction
    # -------------------------------------------------------------------------
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            uv = self._uv_at(event.pos())
            if uv is not None:
                self.picked.emit(*uv)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            uv = self._uv_at(event.pos())
            if uv is not None:
                self.picked.emit(*uv)

    # -------------------------------------------------------------------------
    # Painting
    # -------------------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(35, 35, 40))

        if self._pixmap.isNull():
            painter.setPen(QPen(QColor(200, 200, 200)))
            painter.drawText(self.rect(), Qt.AlignCenter, "No image loaded")
            return

        rect = self.image_rect()
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.drawPixmap(rect, self._pixmap)

        if self._settings is None:
            return

        painter.setRenderHint(QPainter.Antialiasing, True)
        self._draw_horizon(painter, rect)
        self._draw_cardinals(painter, rect)
        self._draw_shadow_mark(painter, rect)
        self._draw_sun(painter, rect)
        painter.setPen(QPen(QColor(255, 255, 255, 90)))
        painter.drawRect(rect.adjusted(0, 0, -1, -1))

    def _draw_horizon(self, painter, rect):
        y = rect.y() + rect.height() // 2
        pen = QPen(_HORIZON_COLOR, 1, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(rect.x(), y, rect.right(), y)
        painter.drawText(rect.x() + 6, y - 5, "horizon")

    def _draw_cardinals(self, painter, rect):
        font = QFont(painter.font())
        font.setBold(True)
        painter.setFont(font)

        for quarter_turns, name in enumerate(_CARDINAL_NAMES):
            u = self._settings.cardinal_u(quarter_turns)
            x = self._point_at(u, 0.0).x()
            is_north = (quarter_turns == 0)
            color = _NORTH_COLOR if is_north else _CARDINAL_COLOR
            painter.setPen(QPen(color, 2 if is_north else 1, Qt.SolidLine if is_north else Qt.DashLine))
            painter.drawLine(x, rect.y(), x, rect.bottom())

            label = f" {name} "
            metrics = painter.fontMetrics()
            width = metrics.horizontalAdvance(label)
            height = metrics.height()
            # Keep the label inside the image even when its direction sits on an edge.
            left = min(max(x - width // 2, rect.x()), rect.right() - width)
            box = QRect(left, rect.bottom() - height - 4, width, height)
            painter.setBrush(QBrush(QColor(0, 0, 0, 170)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(box)
            painter.setPen(QPen(color))
            painter.drawText(box, Qt.AlignCenter, label)

        painter.setBrush(Qt.NoBrush)

    def _draw_shadow_mark(self, painter, rect):
        """Arrow on the horizon pointing where the shadows will fall."""
        u, _ = SB.direction_to_uv(-self._settings.sun_direction(), self._settings.north_u)
        center = self._point_at(u, 0.5)
        painter.setPen(QPen(_SHADOW_COLOR, 2))
        painter.setBrush(QBrush(_SHADOW_COLOR))
        size = 7
        painter.drawPolygon(QPoint(center.x(), center.y() + size),
                            QPoint(center.x() - size, center.y() - size),
                            QPoint(center.x() + size, center.y() - size))
        painter.setBrush(Qt.NoBrush)
        # Below the horizon line, so it never runs into the "horizon" label.
        painter.drawText(center.x() + size + 4, center.y() + size + painter.fontMetrics().height(), "shadow")

    def _draw_sun(self, painter, rect):
        center = self._point_at(self._settings.sun_u, self._settings.sun_v)

        painter.setPen(QPen(QColor(_SUN_COLOR.red(), _SUN_COLOR.green(), _SUN_COLOR.blue(), 150), 1, Qt.DashLine))
        painter.drawLine(rect.x(), center.y(), rect.right(), center.y())
        painter.drawLine(center.x(), center.y(), center.x(), rect.y() + rect.height() // 2)

        painter.setPen(QPen(QColor(40, 40, 40), 3))
        painter.drawEllipse(center, 8, 8)
        painter.setPen(QPen(_SUN_COLOR, 2))
        painter.setBrush(QBrush(QColor(255, 235, 150, 200)))
        painter.drawEllipse(center, 8, 8)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, 15, 15)


class SkyboxDialog(QDialog):
    """
    Modeless editor for the skybox: image file, north reference and sun position.

    While it is open every change is pushed to 'preview_callback' so the 3D scene follows
    along, and rejecting the dialog pushes the settings it started from back.
    """

    def __init__(self, settings, parent=None, preview_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Skybox")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._initial = settings.copy()
        self._settings = settings.copy()
        self._preview_callback = preview_callback
        self._source_image = QImage()
        self._failed_preview_path = None

        self._build_ui()
        self._load_image(self._settings.path, reset_marks=False)
        self._refresh()

    # -------------------------------------------------------------------------
    # Construction
    # -------------------------------------------------------------------------
    def _build_ui(self):
        self.canvas = SkyboxImageCanvas(self)
        self.canvas.picked.connect(self._on_picked)

        self.path_label = QLabel(self)
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        browse_button = QPushButton("Browse...", self)
        browse_button.clicked.connect(self._on_browse)
        default_button = QPushButton("Use default", self)
        default_button.clicked.connect(self._on_use_default)

        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Image:", self))
        file_row.addWidget(self.path_label, 1)
        file_row.addWidget(browse_button)
        file_row.addWidget(default_button)

        self.warning_label = QLabel(self)
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet("color: #b36b00;")
        self.warning_label.hide()

        pick_group = QGroupBox("Click on the image to set", self)
        self.radio_north = QRadioButton("North direction", self)
        self.radio_east = QRadioButton("East direction", self)
        self.radio_sun = QRadioButton("Sun position (sky only)", self)
        self.radio_sun.setChecked(True)
        for radio in (self.radio_north, self.radio_east, self.radio_sun):
            radio.toggled.connect(self._refresh)
        pick_layout = QVBoxLayout()
        pick_layout.addWidget(self.radio_north)
        pick_layout.addWidget(self.radio_east)
        pick_layout.addWidget(self.radio_sun)
        pick_group.setLayout(pick_layout)

        self.hint_label = QLabel(self)
        self.hint_label.setWordWrap(True)
        self.hint_label.setStyleSheet("color: #666666;")

        self.readout_label = QLabel(self)
        self.readout_label.setTextFormat(Qt.RichText)
        self.readout_label.setWordWrap(True)
        self.readout_label.setFrameShape(QFrame.StyledPanel)
        self.readout_label.setMargin(8)

        detect_button = QPushButton("Auto-detect sun", self)
        detect_button.clicked.connect(self._on_auto_detect_sun)
        reset_button = QPushButton("Reset marks", self)
        reset_button.clicked.connect(self._on_reset_marks)

        side = QVBoxLayout()
        side.addWidget(pick_group)
        side.addWidget(self.hint_label)
        side.addWidget(self.readout_label)
        side.addWidget(detect_button)
        side.addWidget(reset_button)
        side.addStretch(1)

        body = QHBoxLayout()
        body.addWidget(self.canvas, 1)
        side_widget = QWidget(self)
        side_widget.setLayout(side)
        side_widget.setFixedWidth(330)
        body.addWidget(side_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(file_row)
        layout.addWidget(self.warning_label)
        layout.addLayout(body)
        layout.addWidget(buttons)
        self.resize(1080, 620)

    # -------------------------------------------------------------------------
    # Image handling
    # -------------------------------------------------------------------------
    def _load_image(self, path, reset_marks=True):
        """
        Show 'path' in the canvas and, unless told otherwise, re-place the marks on it.

        Returns:
            (bool): True if the image could be read.
        """
        image = QImage(path)
        if image.isNull():
            QMessageBox.critical(self, "Skybox", f"Could not read the image:\n{path}")
            return False

        self._source_image = image
        self._settings.path = path

        if reset_marks:
            self._settings.north_u = SB.DEFAULT_NORTH_U
            sun_u, sun_v = guess_sun_uv(image)
            self._settings.sun_u = sun_u
            self._settings.sun_v = min(sun_v, SB.MIN_PICKABLE_SUN_V)

        preview = image
        if image.width() > MAX_PREVIEW_WIDTH:
            preview = image.scaledToWidth(MAX_PREVIEW_WIDTH, Qt.SmoothTransformation)
        self.canvas.set_pixmap(QPixmap.fromImage(preview))

        aspect = image.width() / float(image.height())
        if abs(aspect - 2.0) > 0.05:
            self.warning_label.setText(
                f"This image is {image.width()}x{image.height()} (aspect {aspect:.2f}). "
                "Equirectangular skyboxes are expected to be 2:1, so it will be stretched "
                "onto the sky dome and the marks below may not line up with the horizon.")
            self.warning_label.show()
        else:
            self.warning_label.hide()

        return True

    # -------------------------------------------------------------------------
    # Slots
    # -------------------------------------------------------------------------
    def _on_browse(self):
        start_dir = os.path.dirname(self._settings.path) or ""
        path, _ = QFileDialog.getOpenFileName(self, "Select skybox image", start_dir, IMAGE_FILTER)
        if not path:
            return

        if not SB.is_vtk_readable(path):
            QMessageBox.critical(self, "Skybox",
                                 "VTK cannot read this image format, so it cannot be used as a "
                                 f"skybox:\n{path}\n\nPNG or JPEG images work best.")
            return

        if self._load_image(path, reset_marks=True):
            self._refresh()

    def _on_use_default(self):
        if self._load_image(SB.DEFAULT_SKYBOX_PATH, reset_marks=False):
            self._settings.north_u = SB.DEFAULT_NORTH_U
            self._settings.sun_u = SB.DEFAULT_SUN_U
            self._settings.sun_v = SB.DEFAULT_SUN_V
            self._refresh()

    def _on_auto_detect_sun(self):
        sun_u, sun_v = guess_sun_uv(self._source_image)
        self._settings.sun_u = sun_u
        self._settings.sun_v = min(sun_v, SB.MIN_PICKABLE_SUN_V)
        self._refresh()

    def _on_reset_marks(self):
        self._settings.north_u = SB.DEFAULT_NORTH_U
        self._on_auto_detect_sun()

    def _on_picked(self, u, v):
        if self.radio_north.isChecked():
            self._settings.north_u = u % 1.0
        elif self.radio_east.isChecked():
            # North sits a quarter of the image to the left of east.
            self._settings.north_u = (u - 0.25) % 1.0
        else:
            self._settings.sun_u = u % 1.0
            self._settings.sun_v = min(v, SB.MIN_PICKABLE_SUN_V)
        self._refresh()

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------
    def _refresh(self):
        self.path_label.setText(os.path.basename(self._settings.path))
        self.path_label.setToolTip(self._settings.path)
        self.canvas.set_settings(self._settings)

        if self.radio_sun.isChecked():
            self.hint_label.setText("Click the centre of the sun. Clicks below the horizon "
                                    "are pulled back up into the sky.")
        else:
            self.hint_label.setText("Only the horizontal position of the click matters; it "
                                    "sets which column of the image the scene looks at.")

        sun = self._settings.sun_direction()
        offset_x, offset_y = self._settings.shadow_offset(1.0)
        self.readout_label.setText(
            "<b>North</b> at image column {north:.3f}<br>"
            "<b>Sun</b> azimuth {sun_az:.1f}&deg;, elevation {sun_el:.1f}&deg;<br>"
            "<b>Shadows</b> cast towards {shadow_az:.1f}&deg;<br>"
            "<span style='color:#666666'>{ratio:.2f} m of shadow per m of altitude<br>"
            "sun direction ({dx:.3f}, {dy:.3f}, {dz:.3f}) ENU</span>".format(
                north=self._settings.north_u,
                sun_az=self._settings.sun_azimuth_deg(),
                sun_el=self._settings.sun_elevation_deg(),
                shadow_az=self._settings.shadow_azimuth_deg(),
                ratio=(offset_x ** 2 + offset_y ** 2) ** 0.5,
                dx=sun[0], dy=sun[1], dz=sun[2]))

        self._emit_preview(self._settings)

    def _emit_preview(self, settings):
        if self._preview_callback is None:
            return
        try:
            self._preview_callback(settings.copy())
            self._failed_preview_path = None
        except Exception as error:
            # Dragging a mark previews on every mouse move, so an image the scene refuses
            # to load is only reported the first time it is tried.
            if self._failed_preview_path != settings.path:
                self._failed_preview_path = settings.path
                QMessageBox.critical(self, "Skybox", f"Could not apply the skybox:\n{error}")

    # -------------------------------------------------------------------------
    # Result
    # -------------------------------------------------------------------------
    def settings(self):
        """Settings currently shown by the dialog."""
        return self._settings.copy()

    def reject(self):
        self._emit_preview(self._initial)
        super().reject()


# Standalone runner
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SkyboxDialog(SB.SkyboxSettings(), preview_callback=lambda s: print(s))
    if dialog.exec_() == QDialog.Accepted:
        print("accepted:", dialog.settings())
    else:
        print("cancelled")
