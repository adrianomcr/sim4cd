#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import tkinter as tk
from tkinter import filedialog, ttk
import json
from ttkthemes import ThemedTk

class JsonViewerApp:
    def __init__(self, root):
        self.root = root 
        
        self.tree = ttk.Treeview(root, columns=("Value", "Unit", "Description"), height=20)
        self.tree.heading("#1", text="Value")
        self.tree.heading("#2", text="Unit")
        self.tree.heading("#3", text="Description")
        
        self.tree.bind("<<TreeviewSelect>>", self.update_details)

        self.tree.column("#0", width=150)  # Column 1 (Value) width
        self.tree.column("#1", width=120)  # Column 1 (Value) width
        self.tree.column("#2", width=100)  # Column 2 (Description) width
        self.tree.column("#3", width=400)   # Column 3 (Unit) width

        self.tree.pack(side=tk.LEFT, padx=10)
        

        # Right pannel
        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.LEFT, padx=10)


        # Buttons to load and save file
        buttons = ttk.Frame(right_frame)
        buttons.pack(side=tk.TOP, padx=10)

        self.load_button = ttk.Button(buttons, text="Load", command=self.load_json)
        self.load_button.pack(pady=10, side=tk.LEFT)

        self.save_button = ttk.Button(buttons, text="Save", command=self.save_json)
        self.save_button.pack(pady=10, side=tk.LEFT)

        self.saveas_button = ttk.Button(buttons, text="Save As", command=self.saveas_json)
        self.saveas_button.pack(pady=10, side=tk.LEFT)
        

        # Detailed info about a arameter
        self.details_frame = ttk.Frame(right_frame)
        self.details_frame.pack(side=tk.LEFT, padx=10)
        
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("TkDefaultFont", 12, "bold"))
        self.parameter_label = ttk.Label(self.details_frame, text="Parameter Details", style="Bold.TLabel")
        self.parameter_label.pack(pady=10)
        
        self.description_label = ttk.Label(self.details_frame, text="Description:", wraplength=250)
        self.description_label.pack()
        
        # Create an editable Entry widget for the "Value" field
        self.value_entry = ttk.Entry(self.details_frame)
        self.value_entry.pack()
        
        self.default_label = ttk.Label(self.details_frame, text="Default:")
        self.default_label.pack()
        
        self.type_label = ttk.Label(self.details_frame, text="Type:")
        self.type_label.pack()
        
        self.unit_label = ttk.Label(self.details_frame, text="Unit:")
        self.unit_label.pack()
        
        # Add a "Set" button to save the edited value
        self.set_button = ttk.Button(self.details_frame, text="Set", command=self.set_value)
        self.set_button.pack(pady=10)

        self.file_path = False
        
        self.data = {}  # Store loaded JSON data
        
    def load_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
            
            self.populate_tree()
            
    def populate_tree(self):
        self.tree.delete(*self.tree.get_children())
        for param, details in self.data.items():
            description = details["description"]
            value = details["value"]
            # default = details["default"]
            # data_type = details["type"]
            unit = details["unit"]
            
            # self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            self.tree.insert("", "end", text=param, values=(value, unit, description))


    def update_tree(self,key,value):
        for param, details in self.data.items():
            description = details["description"]
            value = details["value"]
            # default = details["default"]
            # data_type = details["type"]
            unit = details["unit"]
            
            # self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            self.tree.insert("", "end", text=param, values=(value, description, unit))


    def update_details(self, event):
        selected_items = self.tree.selection()
        print(selected_items)
        if selected_items:
            selected_item = selected_items[0]
            selected_param = self.tree.item(selected_item, "text")
            details = self.data[selected_param]

            self.description_label.config(text=f"Description: {details['description']}")
            self.value_entry.delete(0, tk.END)
            self.value_entry.insert(0, details['value'])
            self.default_label.config(text=f"Default: {details['default']}")
            self.type_label.config(text=f"Type: {details['type']}")
            self.unit_label.config(text=f"Unit: {details['unit']}")
        else:
            self.description_label.config(text="Description: ")
            self.value_entry.delete(0, tk.END)
            # self.value_entry.insert(0, details['value'])
            self.default_label.config(text="Default: ")
            self.type_label.config(text="Type: ")
            self.unit_label.config(text="Unit: ")


    def convert_data_type(self,value_str,type_str):

        valid = True
        if(type_str=="int"):
            value = int(round(float(value_str)))
        elif(type_str=="float"):
            value = float(value_str)
        elif(type_str=="bool"):
            value = bool(int(round(float(value_str))))
        else:
            value = None

        return valid, value


    def saveas_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            self.save_json()

    def save_json(self):
        if self.file_path:
            with open(self.file_path, "w") as json_file:
                json.dump(self.data, json_file, indent=4)

    def set_value(self):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = self.tree.selection()[0]
            selected_param = self.tree.item(selected_item, "text")
            valid, new_value = self.convert_data_type(self.value_entry.get(),self.data[selected_param]['type'])
            self.data[selected_param]['value'] = new_value
            self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description']))

            
if __name__ == "__main__":
    root = ThemedTk(theme='black')
    root.title("JSON Viewer")
    app = JsonViewerApp(root)
    # app.tree.bind("<<TreeviewSelect>>", app.update_details)
    root.mainloop()

