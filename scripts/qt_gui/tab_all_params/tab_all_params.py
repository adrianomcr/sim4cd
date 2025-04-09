#!/usr/bin/env python3
import sys
import os
import json

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (
    QWidget, QApplication, QFileDialog, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush


class AllParamsTab(QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)
        self.shared_data = shared_data if shared_data is not None else {}

        # Ensure our shared_data has the needed keys
        if 'config' not in self.shared_data:
            self.shared_data['config'] = {}
        if 'config_file_path' not in self.shared_data:
            self.shared_data['config_file_path'] = ""

        # We no longer keep a separate self.params variable. We directly use self.shared_data['config'].
        # We'll keep a filtered list of keys for display in the table:
        self.filtered_keys = []

        # Load the .ui file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(script_dir, "tab_all_params.ui")
        uic.loadUi(ui_path, self)

        # Hide the combo box for editing values unless needed
        self.comboValue.hide()

        # Connect signals
        self.btnLoad.clicked.connect(self.load_json_file)
        self.btnSave.clicked.connect(self.save_json_file)
        self.btnFilter.clicked.connect(self.filter_params)

        self.tableParams.currentCellChanged.connect(self.on_table_selection_changed)
        # self.tableParams.cellClicked.connect(self.on_table_selection_changed)

        self.btnSetParam.clicked.connect(self.on_set_param)
        self.btnRestoreDefault.clicked.connect(self.on_restore_default)

        # Table is read-only; user edits "value" via the left panel
        self.tableParams.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableParams.setColumnCount(4)
        self.tableParams.setHorizontalHeaderLabels(["Parameter", "Value", "Unit", "Description"])

        # self.tableParams.setFocusPolicy(Qt.StrongFocus)
        # self.tableParams.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.tableParams.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)


        # # somewhere in your table-setup code
        # self.tableParams.setFocusPolicy(Qt.ClickFocus)  # or Qt.ClickFocus, if you still want it focusable
        # self.tableParams.setStyleSheet("""
        #     /* Keep the highlight visible even if the table loses focus: */
        #     QTableView::item:selected {
        #         background: #3399FF;  /* pick the color you want */
        #         color: white;
        #     }
        #     QTableView::item:selected:!active {
        #         background: #3399FF;  /* same color for unfocused state */
        #         color: white;
        #     }
        # # """)


        # If config already has data, show it
        if(not self.shared_data['config'] == None):
            if len(self.shared_data['config']) > 0:
                self.filtered_keys = sorted(self.shared_data['config'].keys())
                self.populate_table()
        self.clear_details()


    # ----------------------------------------------------------------
    # File Load / Save
    # ----------------------------------------------------------------
    def load_json_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Open JSON file", "", "JSON Files (*.json);;All Files (*)"
        )
        if not filepath:
            return
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load JSON:\n{str(e)}")
            return

        # Update shared_data with the loaded config
        self.shared_data['config'] = data
        self.shared_data['config_file_path'] = filepath

        # Reset filter and refresh table
        self.filtered_keys = sorted(self.shared_data['config'].keys())
        self.populate_table()
        self.clear_details()

    def save_json_file(self):
        if not self.shared_data['config']:
            QMessageBox.warning(self, "No data", "No parameters to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save JSON file", "", "JSON Files (*.json);;All Files (*)"
        )
        if not filepath:
            return

        try:
            with open(filepath, "w") as f:
                json.dump(self.shared_data['config'], f, indent=4)
            self.shared_data['config_file_path'] = filepath
            QMessageBox.information(self, "Success", "File saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save JSON:\n{str(e)}")

    # ----------------------------------------------------------------
    # Table / Filtering
    # ----------------------------------------------------------------
    def filter_params(self):
        """Filter the table by substring match in param name."""
        text = self.editFilterParam.text().strip()
        if not text:
            self.filtered_keys = sorted(self.shared_data['config'].keys())
        else:
            self.filtered_keys = [
                k for k in self.shared_data['config'].keys()
                if text.lower() in k.lower()
            ]
            self.filtered_keys.sort()

        self.populate_table()
        self.clear_details()

    def populate_table(self):
        """Populate the table with self.filtered_keys."""
        cfg = self.shared_data['config']

        self.tableParams.blockSignals(True)
        self.tableParams.setRowCount(len(self.filtered_keys))

        for row, key in enumerate(self.filtered_keys):
            data = cfg[key]

            # Column 0: Param name
            param_item = QTableWidgetItem(key)
            # Column 1: value (as string)
            val_str = str(data.get("value", ""))
            value_item = QTableWidgetItem(val_str)
            # Column 2: unit
            unit_str = str(data.get("unit", ""))
            unit_item = QTableWidgetItem(unit_str)
            # Column 3: description
            desc_str = str(data.get("description", ""))
            desc_item = QTableWidgetItem(desc_str)

            self.tableParams.setItem(row, 0, param_item)
            self.tableParams.setItem(row, 1, value_item)
            self.tableParams.setItem(row, 2, unit_item)
            self.tableParams.setItem(row, 3, desc_item)

            # Color row if changed from default
            self.apply_color_if_changed(key, row)

        self.tableParams.resizeColumnsToContents()
        self.tableParams.blockSignals(False)

    def apply_color_if_changed(self, key, row):
        """Color row if value != default."""
        data = self.shared_data['config'][key]
        current_value = data.get("value")
        default_value = data.get("default")

        changed = (str(current_value) != str(default_value))
        color = QColor("white")
        if changed:
            color = QColor("#FFFFCC")  # light yellow

        for col in range(self.tableParams.columnCount()):
            item = self.tableParams.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    # ----------------------------------------------------------------
    # Details Panel
    # ----------------------------------------------------------------
    def clear_details(self):
        self.lblParamName.setText("-")
        self.txtDescription.clear()
        self.lblDefaultValue.setText("-")
        self.lblType.setText("-")
        self.lblUnit.setText("-")
        self.editValue.setText("")
        self.editValue.show()
        self.comboValue.clear()
        self.comboValue.hide()

    def on_table_selection_changed(self, currentRow, currentCol, prevRow, prevCol):
    # def on_table_selection_changed(self, currentRow):
        """
        Called when a row is selected in the table. Display that param in the left panel.
        """
        if currentRow < 0 or currentRow >= len(self.filtered_keys):
            self.clear_details()
            return

        key = self.filtered_keys[currentRow]
        data = self.shared_data['config'].get(key, {})

        # Fill left panel
        self.lblParamName.setText(str(key))
        desc = data.get("description", "")
        self.txtDescription.setText(desc)

        default_val = data.get("default", "")
        self.lblDefaultValue.setText(str(default_val))

        ptype = data.get("type", "")
        self.lblType.setText(str(ptype))

        unit_str = data.get("unit", "")
        self.lblUnit.setText(str(unit_str))

        options = data.get("options", [])
        current_val = data.get("value", "")

        if options and len(options) > 0:
            self.comboValue.clear()
            self.comboValue.addItems([str(x) for x in options])
            self.comboValue.show()
            self.editValue.hide()
            # Attempt to select current_val in combo
            current_str = str(current_val)
            idx = self.comboValue.findText(current_str)
            if idx >= 0:
                self.comboValue.setCurrentIndex(idx)
        else:
            self.editValue.show()
            self.comboValue.hide()
            self.editValue.setText(str(current_val))


        

    def on_set_param(self):
        """User clicked 'Set Parameter'. Validate and store the new value."""
        key = self.lblParamName.text()
        if key == "-" or not key:
            return  # no param selected

        cfg = self.shared_data['config']
        data = cfg.get(key, {})

        ptype = data.get("type", "").lower()
        options = data.get("options", [])

        if self.comboValue.isVisible():
            new_val_str = self.comboValue.currentText().strip()
        else:
            new_val_str = self.editValue.text().strip()

        # If 'options' is not empty, must pick from them
        if options and (new_val_str not in [str(x) for x in options]):
            QMessageBox.warning(self, "Invalid Value",
                                f"'{new_val_str}' is not one of the allowed options.")
            return

        if not self.validate_value(new_val_str, ptype):
            QMessageBox.warning(self, "Invalid Value",
                                f"'{new_val_str}' is not a valid {ptype} value.")
            return

        parsed_val = self.parse_value(new_val_str, ptype)
        data["value"] = parsed_val
        cfg[key] = data  # update shared_data['config']

        # Update row in table
        self.update_table_row(key)
        QMessageBox.information(self, "Updated", f"Parameter '{key}' updated.")

    def on_restore_default(self):
        """Restore parameter's default value."""
        key = self.lblParamName.text()
        if key == "-" or not key:
            return

        cfg = self.shared_data['config']
        data = cfg.get(key, {})

        default_val = data.get("default")
        ptype = data.get("type", "").lower()
        options = data.get("options", [])

        data["value"] = default_val
        cfg[key] = data  # store updated data back

        # Update left panel
        if options:
            default_str = str(default_val)
            idx = self.comboValue.findText(default_str)
            if idx >= 0:
                self.comboValue.setCurrentIndex(idx)
            else:
                self.comboValue.addItem(default_str)
                self.comboValue.setCurrentIndex(self.comboValue.count() - 1)
        else:
            self.editValue.setText(str(default_val))

        # Update row in table
        self.update_table_row(key)

    def update_table_row(self, key):
        """Update the 'value' column and row color for the given key."""
        if key not in self.filtered_keys:
            return
        row_index = self.filtered_keys.index(key)

        cfg = self.shared_data['config']
        data = cfg[key]
        new_val_str = str(data.get("value", ""))

        item_val = self.tableParams.item(row_index, 1)
        if item_val:
            item_val.setText(new_val_str)

        self.apply_color_if_changed(key, row_index)

    # ----------------------------------------------------------------
    # Type Handling
    # ----------------------------------------------------------------
    def validate_value(self, val_str, ptype):
        """Check whether val_str can be interpreted as ptype (int, float, bool)."""
        if ptype == "int":
            try:
                f = float(val_str)
                if not f.is_integer():
                    return False
            except ValueError:
                return False
        elif ptype == "float":
            try:
                float(val_str)
            except ValueError:
                return False
        elif ptype == "bool":
            if val_str.lower() not in ("true", "false"):
                return False
        # fallback: no strict check
        return True

    def parse_value(self, val_str, ptype):
        """Convert val_str to the correct Python type."""
        if ptype == "int":
            return int(float(val_str))
        elif ptype == "float":
            return float(val_str)
        elif ptype == "bool":
            return (val_str.lower() == "true")
        return val_str

# ---------------------------------------------------------------
# Standalone test harness
# ---------------------------------------------------------------
if __name__ == "__main__":
    # Example usage: suppose we have an existing shared_data dict
    example_shared_data = {
        'config': {
            "MY_INT_PARAM": {
                "description": "An integer param",
                "value": 2,
                "default": 1,
                "options": [],
                "type": "int",
                "unit": ""
            }
        },
        'config_file_path': ""
    }

    app = QApplication(sys.argv)
    w = AllParamsTab(shared_data=example_shared_data)
    w.show()
    sys.exit(app.exec_())
