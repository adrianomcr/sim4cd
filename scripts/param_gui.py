#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import filedialog, ttk
import json
from ttkthemes import ThemedTk

class JsonViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Viewer")
        
        self.load_button = ttk.Button(root, text="Load JSON File", command=self.load_json)
        self.load_button.pack(pady=10, side=tk.RIGHT)

        self.save_button = ttk.Button(root, text="Save", command=self.save_json)
        self.save_button.pack(pady=10, side=tk.RIGHT)

        self.saveas_button = ttk.Button(root, text="Save As", command=self.saveas_json)
        self.saveas_button.pack(pady=10, side=tk.RIGHT)
        

        # self.load_button = tk.Button(root, text="Load JSON File", command=self.load_json)
        # self.load_button.pack(pady=10, side=tk.LEFT)  # Placed on the left
        
        # self.set_button = tk.Button(root, text="Set", command=self.set_value)
        # self.set_button.pack(pady=10, side=tk.LEFT)  # Placed on the left
        
        # self.save_button = tk.Button(root, text="Save As", command=self.save_json)
        # self.save_button.pack(pady=10, side=tk.LEFT)  # Placed on the left
        

        # self.tree = ttk.Treeview(root, columns=("Description", "Value", "Default", "Type", "Unit"))
        # self.tree.heading("#1", text="Description")
        # self.tree.heading("#2", text="Value")
        # self.tree.heading("#3", text="Default")
        # self.tree.heading("#4", text="Type")
        # self.tree.heading("#5", text="Unit")
        self.tree = ttk.Treeview(root, columns=("Value", "Description", "Unit"))
        self.tree.heading("#1", text="Value")
        self.tree.heading("#2", text="Description")
        self.tree.heading("#3", text="Unit")

        self.tree.pack(side=tk.LEFT, padx=10)
        
        self.details_frame = ttk.Frame(root)
        self.details_frame.pack(side=tk.LEFT, padx=10)
        
        self.parameter_label = ttk.Label(self.details_frame, text="Parameter Details:")
        self.parameter_label.pack(pady=10)
        
        self.description_label = ttk.Label(self.details_frame, text="Description:")
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
            self.tree.insert("", "end", text=param, values=(value, description, unit))


    def update_tree(self,key,value):
        for param, details in self.data.items():
            description = details["description"]
            value = details["value"]
            # default = details["default"]
            # data_type = details["type"]
            unit = details["unit"]
            
            # self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            self.tree.insert("", "end", text=param, values=(value, description, unit))



            
    # def update_details(self, event):
    #     # print('\33[91m',event,'\33[0m')
    #     selected_item = self.tree.selection()[0]
    #     selected_param = self.tree.item(selected_item, "text")
    #     details = self.data[selected_param]
        
    #     self.description_label.config(text=f"Description: {details['description']}")
    #     self.value_entry.delete(0, tk.END)
    #     self.value_entry.insert(0, details['value'])
    #     self.default_label.config(text=f"Default: {details['default']}")
    #     self.type_label.config(text=f"Type: {details['type']}")
    #     self.unit_label.config(text=f"Unit: {details['unit']}")

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

    def saveas_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            self.save_json()

    def save_json(self):
        if self.file_path:
            with open(self.file_path, "w") as json_file:
                json.dump(self.data, json_file, indent=4)
        
    # def set_value(self):
    #     selected_item = self.tree.selection()[0]
    #     selected_param = self.tree.item(selected_item, "text")
    #     new_value = self.value_entry.get()
        
    #     # Update the value in self.data
    #     self.data[selected_param]['value'] = new_value

    #     # # Update the value in self.data
    #     # self.data[selected_param]['value'] = new_value
    #     # file_path = "./out.json"
    #     # if file_path:
    #     #     with open(file_path, "w") as json_file:
    #     #         json.dump(self.data, json_file, indent=4)

    #     # Update the Treeview
    #     self.populate_tree()
    #     # self.save_json()


    def set_value(self):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = self.tree.selection()[0]
            selected_param = self.tree.item(selected_item, "text")
            new_value = self.value_entry.get()
            self.data[selected_param]['value'] = new_value
            self.tree.item(selected_item, values=(new_value, self.data[selected_param]['description'], self.data[selected_param]['unit']))

            
if __name__ == "__main__":
    # root = tk.Tk()
    root = ThemedTk(theme='black')
    app = JsonViewerApp(root)
    app.tree.bind("<<TreeviewSelect>>", app.update_details)
    root.mainloop()



# import tkinter as tk
# from tkinter import filedialog, ttk
# import json

# class JsonViewerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("JSON Viewer")
        
#         self.load_button = tk.Button(root, text="Load JSON File", command=self.load_json)
#         self.load_button.pack(pady=10)
        
#         self.tree = ttk.Treeview(root, columns=("Description", "Value", "Default", "Type", "Unit"))
#         self.tree.heading("#1", text="Description")
#         self.tree.heading("#2", text="Value")
#         self.tree.heading("#3", text="Default")
#         self.tree.heading("#4", text="Type")
#         self.tree.heading("#5", text="Unit")
#         self.tree.pack(side=tk.LEFT, padx=10)
        
#         self.details_frame = tk.Frame(root)
#         self.details_frame.pack(side=tk.LEFT, padx=10)
        
#         self.parameter_label = tk.Label(self.details_frame, text="Parameter Details:")
#         self.parameter_label.pack(pady=10)
        
#         self.description_label = tk.Label(self.details_frame, text="Description:")
#         self.description_label.pack()
        
#         self.value_label = tk.Label(self.details_frame, text="Value:")
#         self.value_label.pack()
        
#         self.default_label = tk.Label(self.details_frame, text="Default:")
#         self.default_label.pack()
        
#         self.type_label = tk.Label(self.details_frame, text="Type:")
#         self.type_label.pack()
        
#         self.unit_label = tk.Label(self.details_frame, text="Unit:")
#         self.unit_label.pack()
        
#         self.save_button = tk.Button(root, text="Save As", command=self.save_json)
#         self.save_button.pack(pady=10)
        
#         self.data = {}  # Store loaded JSON data
        
#     def load_json(self):
#         file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
#         if file_path:
#             with open(file_path, "r") as json_file:
#                 self.data = json.load(json_file)
            
#             self.populate_tree()
            
#     def populate_tree(self):
#         self.tree.delete(*self.tree.get_children())
#         for param, details in self.data.items():
#             description = details["description"]
#             value = details["value"]
#             default = details["default"]
#             data_type = details["type"]
#             unit = details["unit"]
            
#             self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            
#     def update_details(self, event):
#         selected_item = self.tree.selection()[0]
#         selected_param = self.tree.item(selected_item, "text")
#         details = self.data[selected_param]
        
#         self.description_label.config(text=f"Description: {details['description']}")
#         self.value_label.config(text=f"Value: {details['value']}")
#         self.default_label.config(text=f"Default: {details['default']}")
#         self.type_label.config(text=f"Type: {details['type']}")
#         self.unit_label.config(text=f"Unit: {details['unit']}")
        
#     def save_json(self):
#         file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
#         if file_path:
#             with open(file_path, "w") as json_file:
#                 json.dump(self.data, json_file, indent=4)
            
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = JsonViewerApp(root)
#     app.tree.bind("<<TreeviewSelect>>", app.update_details)
#     root.mainloop()




# import tkinter as tk
# from tkinter import filedialog
# import json
# from tkinter import ttk

# class JsonViewerApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("JSON Viewer")
        
#         self.load_button = tk.Button(root, text="Load JSON File", command=self.load_json)
#         self.load_button.pack(pady=10)
        
#         self.tree = ttk.Treeview(root, columns=("Description", "Value", "Default", "Type", "Unit"))
#         self.tree.heading("#1", text="Description")
#         self.tree.heading("#2", text="Value")
#         self.tree.heading("#3", text="Default")
#         self.tree.heading("#4", text="Type")
#         self.tree.heading("#5", text="Unit")
#         self.tree.pack()
        
#     def load_json(self):
#         file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
#         if file_path:
#             with open(file_path, "r") as json_file:
#                 data = json.load(json_file)
            
#             for param, details in data.items():
#                 description = details["description"]
#                 value = details["value"]
#                 default = details["default"]
#                 data_type = details["type"]
#                 unit = details["unit"]
                
#                 self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = JsonViewerApp(root)
#     root.mainloop()






