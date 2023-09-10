#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to edit the parameter values

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os


class JsonViewerApp:
    def __init__(self, root):
        self.root = root

        try:
            # Define and set a parameters icon for the GUI
            photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/params_icon.png')
            root.iconphoto(False, photo)
        except Exception as e:
            print("An error occurred while creating the icon:", e)
        
        self.tree = ttk.Treeview(root, columns=("Value", "Unit", "Description"), height=20)
        self.tree.heading("#0", text="    Parameter", anchor=tk.W)
        self.tree.heading("#1", text="Value", anchor=tk.W)
        self.tree.heading("#2", text="Unit", anchor=tk.W)
        self.tree.heading("#3", text="Description", anchor=tk.W)
        
        self.tree.bind("<<TreeviewSelect>>", self.update_details)

        self.tree.column("#0", minwidth=200, width=200, stretch=tk.NO)  # Column 0 (Name)
        self.tree.column("#1", minwidth=120, width=120, stretch=tk.NO)  # Column 1 (Value)
        self.tree.column("#2", minwidth=100, width=100, stretch=tk.NO)  # Column 2 (Unit)
        self.tree.column("#3", minwidth=400)                            # Column 3 (Description)

        self.tree.pack(side=tk.LEFT)

        # Create a vertical scrollbar and attach it to the Treeview
        v_scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        # Pack the Treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill="y")



        # Right panel
        right_frame = ttk.Frame(root)
        right_frame.pack(side=tk.LEFT, fill="both", expand=False)


        # Buttons to load and save file
        buttons = ttk.Frame(right_frame)
        buttons.pack(side=tk.TOP, padx=10)

        self.load_button = ttk.Button(buttons, text="    Load", padding=(4, 4), command=self.load_json)
        self.load_button.pack(pady=10, side=tk.LEFT)

        self.save_button = ttk.Button(buttons, text="    Save", padding=(4, 4), command=self.save_json)
        self.save_button.pack(pady=10, side=tk.LEFT)

        self.saveas_button = ttk.Button(buttons, text="  Save As", padding=(4, 4), command=self.saveas_json)
        self.saveas_button.pack(pady=10, side=tk.LEFT)
        

        # Detailed info about a arameter
        self.details_frame = ttk.Frame(right_frame)
        self.details_frame.pack(side=tk.TOP, padx=10)
        
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("TkDefaultFont", 12, "bold"))
        self.parameter_label = ttk.Label(self.details_frame, text="Parameter Details", style="Bold.TLabel")
        self.parameter_label.pack(pady=10)

        self.name_label = ttk.Label(self.details_frame, text="", style="Bold.TLabel")
        self.name_label.pack(pady=2)

        self.combobox = ttk.Combobox(self.details_frame, values=[])
        self.combobox.bind("<<ComboboxSelected>>", self.on_option_selected)
        self.combobox.set("")
        self.combobox.pack(pady=2)

        self.description_label = ttk.Label(self.details_frame, text=f"Description:", wraplength=250)
        self.description_label.pack(pady=2)

        self.default_label = ttk.Label(self.details_frame, text="Default:")
        self.default_label.pack(pady=2)
        
        self.type_label = ttk.Label(self.details_frame, text="Type:")
        self.type_label.pack(pady=2)
        
        self.unit_label = ttk.Label(self.details_frame, text="Unit:")
        self.unit_label.pack(pady=2)
        

        # Checkbox to automatically save to a JSON file        
        self.checkbox_state = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(right_frame, text="Auto Save", variable=self.checkbox_state)#, command=on_checkbox_toggle)
        self.checkbox.pack(pady=10, side=tk.BOTTOM)

        # Buttons Set new values and restore default
        self.set_buttons_frame = ttk.Frame(right_frame)
        self.set_buttons_frame.pack(side=tk.BOTTOM, padx=10)

        # Add a "Set" button to save the edited value
        self.set_button = ttk.Button(self.set_buttons_frame, text="      Set", padding=(4, 4), command=self.set_value)
        self.set_button.pack(padx=5, side=tk.LEFT)
        # Add a "Restore default" button to save the edited value
        self.set_default_button = ttk.Button(self.set_buttons_frame, text="  Restore", padding=(4, 4), command=self.set_default_value)
        self.set_default_button.pack(padx=5, side=tk.LEFT)

        self.file_path = False
        
        self.data = {}  # Store loaded JSON data
        

    def on_option_selected(self, event):
        return


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
            description = details["description"].split('\n')[0]
            value = details["value"]
            # default = details["default"]
            # data_type = details["type"]
            unit = details["unit"]
            
            # # self.tree.insert("", "end", text=param, values=(description, value, default, data_type, unit))
            # self.tree.insert("", "end", text=param, values=(value, unit, description))

            self.tree.tag_configure("different", foreground="#FFAA50")
            self.tree.tag_configure("white", foreground="white")

            # .........
            if value == details["default"]:
                self.tree.insert("", "end", text=param, values=(value, unit, description))
            else:
                self.tree.insert("", "end", text=param, values=(value, unit, description), tags=("different",))
                

    def update_details(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            selected_param = self.tree.item(selected_item, "text")
            details = self.data[selected_param]

            self.description_label.config(text=f"Description: {details['description']}")
            self.combobox.delete(0, tk.END)
            self.combobox.insert(0, str(details['value']))
            self.combobox['values'] = details['options']
            self.name_label.config(text=selected_param)
            self.default_label.config(text=f"Default: {details['default']}")
            self.type_label.config(text=f"Type: {details['type']}")
            self.unit_label.config(text=f"Unit: {details['unit']}")
        else:
            self.description_label.config(text="Description: ")
            self.combobox.delete(0, tk.END)
            self.combobox['values'] = []
            self.name_label.config(text=f"")
            self.default_label.config(text="Default: ")
            self.type_label.config(text="Type: ")
            self.unit_label.config(text="Unit: ")


    def convert_data_type(self,value_str,type_str):

        valid = True
        try:
            if(type_str=="int"):
                value = int(round(float(value_str)))
            elif(type_str=="float"):
                value = float(value_str)
            elif(type_str=="bool"):
                true_list = ['1', '+1', 'true', 't']
                s = str(type_str).lower()
                value = True if s in true_list else False
            else:
                value = None
        except:
            messagebox.showerror("Error", "Value not valid\nCheck if it is a " + type_str)
            value = 0
            valid = False

        return valid, value


    def check_value(self,value_str,type_str,options):

        valid_type, value = self.convert_data_type(value_str,type_str)

        valid = valid_type
        if(valid):
            print('valid type')
            if(options):
                print('has options')
                if(not value in options):
                    valid = False
                    print('invalid option')
                    messagebox.showerror("Error", "Value inserted is not a valid option")
                else:
                    print('valid option')

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
            valid, new_value = self.check_value(self.combobox.get(),self.data[selected_param]['type'],self.data[selected_param]['options'])
            if(not valid):
                return

            self.data[selected_param]['value'] = new_value

            # .........
            if new_value == self.data[selected_param]["default"]:
                self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("white",))
            else:
                self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("different",))

            if(self.auto_save()):
                self.save_json()

    def auto_save(self):
        return self.checkbox_state.get()

    def set_default_value(self):
        selected_items = self.tree.selection()
        # if selected_items:
        for selected_item in selected_items:
            # selected_item = self.tree.selection()[0]
            selected_param = self.tree.item(selected_item, "text")
            new_value = self.data[selected_param]['default']
            self.data[selected_param]['value'] = new_value
            self.combobox.delete(0, tk.END)
            self.combobox.insert(0, str(new_value))
            self.combobox['values'] = self.data[selected_param]['options']
            self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("white",))

        if(self.auto_save() and selected_items):
            self.save_json()


if __name__ == "__main__":
    """
    Main to run a detached JsonViewerApp window
    """

    # Define root GUI window
    root = ThemedTk(theme='black')
    # Define GUI title
    root.title("Parameters Editor")
    # Define GUI window size
    root.geometry('1150x450')

    # Create the GUI object
    app = JsonViewerApp(root)

    # Run the tkinter event loop
    root.mainloop()

