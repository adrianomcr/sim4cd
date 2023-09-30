#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to edit the parameter values

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
from fnmatch import fnmatch


class JsonEditorGUI:
    """
    Class that defines a GUI for editing the parameters
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the dynamics class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
            enable_io_ (bool): Flag to enable the creation of input/output buttons to the gui
        """

        # Set the root variable
        self.root = root_
        
        # Set the io_enabled variable
        self.io_enabled = enable_io_

        # Initialize the variable to store the json data
        self.data = {}  
        
        # Create a treeview to display the parameters attributes
        self.tree = ttk.Treeview(self.root, columns=("Value", "Unit", "Description"), height=20)
        # Set the headers of each column
        self.tree.heading("#0", text="    Parameter", anchor=tk.W)
        self.tree.heading("#1", text="Value", anchor=tk.W)
        self.tree.heading("#2", text="Unit", anchor=tk.W)
        self.tree.heading("#3", text="Description", anchor=tk.W)
        # Attach the function update_details to the act of selecting a value on the treeview
        self.tree.bind("<<TreeviewSelect>>", self.update_details)
        # Configure the sizes of each column
        self.tree.column("#0", minwidth=200, width=200, stretch=tk.NO)  # Column 0 (Name)
        self.tree.column("#1", minwidth=120, width=120, stretch=tk.NO)  # Column 1 (Value)
        self.tree.column("#2", minwidth=150, width=150, stretch=tk.NO)  # Column 2 (Unit)
        self.tree.column("#3", minwidth=400)                            # Column 3 (Description)
        # Pack the treeview
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        # Define possible colors for the treeview lines
        self.tree.tag_configure("orange", foreground="#FFAA50")
        self.tree.tag_configure("white", foreground="white")

        # Create a vertical scrollbar and attach it to the Treeview
        self.v_scrollbar = tk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)
        # Pack the scrollbar
        self.v_scrollbar.pack(side=tk.RIGHT, fill="y")

        # Define a right panel
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.LEFT, fill="both", expand=False)

        if(self.io_enabled):
            # Create buttons to load and save file
            buttons_frame = ttk.Frame(right_frame)
            buttons_frame.pack(side=tk.TOP, padx=10)
            # Button to load file
            self.load_button = ttk.Button(buttons_frame, text="    Load", padding=(4, 4), command=self.load_json)
            self.load_button.pack(pady=10, side=tk.LEFT)
            # Button to save file
            self.save_button = ttk.Button(buttons_frame, text="    Save", padding=(4, 4), command=self.save_json)
            self.save_button.pack(pady=10, side=tk.LEFT)
            # Button to save file as
            self.saveas_button = ttk.Button(buttons_frame, text="  Save As", padding=(4, 4), command=self.saveas_json)
            self.saveas_button.pack(pady=10, side=tk.LEFT)
        
        # Create a subframe for detailed info about a parameter
        details_frame = ttk.Frame(right_frame)
        details_frame.pack(side=tk.TOP, padx=10)
        # Display the detailed information about a parameter
        style = ttk.Style()
        style.configure("Bold.TLabel", font=("TkDefaultFont", 12, "bold"))
        # Display name of panel
        self.details_frame_label = ttk.Label(details_frame, text="Parameter Details", style="Bold.TLabel")
        self.details_frame_label.pack(pady=10)
        # Display the name of the parameter
        self.name_label = ttk.Label(details_frame, text="", style="Bold.TLabel")
        self.name_label.pack(pady=2)
        # Create an entry to set new parameter values and a dropdown to display options
        self.combobox = ttk.Combobox(details_frame, values=[])
        self.combobox.bind("<<ComboboxSelected>>", self.on_option_selected)
        self.combobox.bind("<Return>", lambda event=None: self.set_value())
        self.combobox.set("")
        self.combobox.pack(pady=2)
        # Display the description of the parameter
        self.description_label = ttk.Label(details_frame, text=f"Description:", wraplength=250)
        self.description_label.pack(pady=2)
        # Display the default value of the parameter
        self.default_label = ttk.Label(details_frame, text="Default:")
        self.default_label.pack(pady=2)
        # Display the type of the parameter
        self.type_label = ttk.Label(details_frame, text="Type:")
        self.type_label.pack(pady=2)
        # Display the unit of the parameter
        self.unit_label = ttk.Label(details_frame, text="Unit:")
        self.unit_label.pack(pady=2)
        
        # Create aheckbox to automatically save to the JSON file
        self.checkbox_state = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(right_frame, text="Auto Save", variable=self.checkbox_state)#, command=on_checkbox_toggle)
        self.checkbox.pack(pady=10, side=tk.BOTTOM)

        # Create a subframe for buttons to set a value and restore a parameter default
        set_buttons_frame = ttk.Frame(right_frame)
        set_buttons_frame.pack(side=tk.BOTTOM, padx=10)
        # Add a "Set" button to save the edited value
        self.set_button = ttk.Button(set_buttons_frame, text="      Set", padding=(4, 4), command=self.set_value)
        self.set_button.pack(padx=5, side=tk.LEFT)
        # Add a "Restore" default button to save the edited value
        self.set_default_button = ttk.Button(set_buttons_frame, text="  Restore", padding=(4, 4), command=self.set_default_value)
        self.set_default_button.pack(padx=5, side=tk.LEFT)

        # Create a subframe for filter entry and button
        filter_frame = ttk.Frame(right_frame)
        filter_frame.pack(side=tk.BOTTOM, pady=10)
        # Create an entry to filter the parameters displayed on the tree
        self.filter_entry = tk.Entry(filter_frame, width=15)
        self.filter_entry.pack(padx=5, side=tk.LEFT)
        # Bind an enter press to the function that repopulates the tree
        self.filter_entry.bind("<Return>", lambda event=None: self.populate_tree_filtered())
        # Create a button to repopulate the tree according to the filter value
        self.set_button = ttk.Button(filter_frame, text="    Filter", padding=(3, 3), command=self.populate_tree_filtered)
        self.set_button.pack(padx=5, side=tk.LEFT)

        # Initialize the variable to store the json path
        self.file_path = False
        

    def set_data(self, d, path):
        """
        Set data dictionary and the file path of the gui
        """
        self.data = d
        self.file_path = path


    def get_data(self):
        """
        Return the current data dictionary that the gui is using
        """
        return self.data


    def viz_return(self):
        """
        Function to update the visualization of the gui
        """
        # Just call the populate_tree() function
        self.populate_tree()
        return


    def on_option_selected(self, event):
        """
        Function that calls the set_value function when a value from the parameter dropdown is selected

        Parameters:
            event (tkinter.Event): Tkinter event (not used)
        """

        # Set the value clicked on the dropdown
        self.set_value()


    def load_json(self):
        """
        Function to show a file dialog to load a json file
        """
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
            
            self.populate_tree()
    

    def populate_tree_filtered(self):
        """
        Function to insert the parameter values on the treeview according to the filter value on the entrybox for the filter
        """

        # Get the filter pattern
        self.pattern = self.filter_entry.get()
        # If the filter is not specific (contains '*'), generalize it by adding '*' before and after
        if(not '*' in self.pattern):
            self.pattern = '*'+self.pattern+'*'
        # Populate the treeview according with the filter pattern
        self.populate_tree(filter_pattern=self.pattern)


    def populate_tree(self, filter_pattern='*'):
        """
        Function to insert the parameter values on the treeview

        Parameters:
            filter_pattern (str): pattern the parameter name needs to fit in in order to be displayed on the treeview
        """

        # Reset the treeview
        self.tree.delete(*self.tree.get_children())

        # For every parameter
        for param_name, param_values in self.data.items():

            # Ignore parameter if it does not match the pattern
            if(not fnmatch(param_name.lower(),filter_pattern.lower())):
                continue

            # Insert the parameter data on the tree
            value = param_values["value"] # Insert current value
            unit = param_values["unit"] # Insert 
            description = param_values["description"].split('\n')[0] # Only insert the first line of the description
            
            # Set the color of the treeview line according if the current value is the default or not
            if value == param_values["default"]:
                # Set white color if parameter has the default value
                self.tree.insert("", "end", text=param_name, values=(value, unit, description), tags=("white",))
            else:
                # Set orange color if parameter does not have the default value
                self.tree.insert("", "end", text=param_name, values=(value, unit, description), tags=("orange",))
                

    def update_details(self, event):
        """
        Function to insert the attributes of the selected parameter n the details frame
        """

        # Get the selected lines on the treeview
        selected_items = self.tree.selection()
        # If at least a line is selected
        if selected_items:
            # Get the first line selected
            selected_item = selected_items[0]
            # Get the name of the parameter
            selected_param = self.tree.item(selected_item, "text")
            # Get the attributes of the parameter
            details = self.data[selected_param]

            # Update the parameter name label
            self.name_label.config(text=selected_param)
            # Update the entry/dropdown to insert new values for the parameter
            self.combobox.delete(0, tk.END)
            self.combobox.insert(0, str(details['value']))
            self.combobox['values'] = details['options']
            # Update the parameter description label
            self.description_label.config(text=f"Description: {details['description']}")
            # Update the parameter default value label
            self.default_label.config(text=f"Default: {details['default']}")
            # Update the parameter type label
            self.type_label.config(text=f"Type: {details['type']}")
            # Update the parameter unit label
            self.unit_label.config(text=f"Unit: {details['unit']}")
        # If no line of the treeview is selected
        else:
            # Reset the details field
            self.description_label.config(text="Description: ")
            self.combobox.delete(0, tk.END)
            self.combobox['values'] = []
            self.name_label.config(text=f"")
            self.default_label.config(text="Default: ")
            self.type_label.config(text="Type: ")
            self.unit_label.config(text="Unit: ")


    def convert_data_type(self,value_str,type_str):
        """
        Function to convert a value in the form os a string to the correct type

        Parameters:
            value_str (string): Parameter value in the form of a string
            type_str (string): Parameter type

        Returns:
            valid (bool): Flag that indicates if the value string was successfully converted to the specified
            value (variable type): Value of the parameter with the type indicated by type_str
        """

        valid = True
        # Try to convert the string value to the specified type
        try:
            # If specified type is integer
            if(type_str=="int"):
                value = int(round(float(value_str)))
            # If specified type is float
            elif(type_str=="float"):
                value = float(value_str)
            # If specified type is boolean
            elif(type_str=="bool"):
                # Define list of (lowercase) strings to be interpreted as true
                true_list = ['1', '+1', 'true', 't']
                # Lowercase the input string
                s = value_str.lower()
                # Convert value to boolean
                value = True if s in true_list else False
            else:
                value = None
        except:
            # Throw an error message if there was a mismatch between the provided string value and the value type
            messagebox.showerror("Error", "Value not valid\nCheck if it is a " + type_str)
            value = 0
            valid = False

        return valid, value


    def check_value(self,value_str,type_str,options):
        """
        Function to validate value in the form os a string and convert it to the correct type

        Parameters:
            value_str (string): Parameter value in the form of a string
            type_str (string): Parameter type
            options (string): List with the possible (limited) parameter options

        Returns:
            valid (bool): Flag that indicates if the value string was successfully converted to the specified
            value (variable type): Value of the parameter with the type indicated by type_str
        """

        # Get the value with the appropriated type
        valid_type, value = self.convert_data_type(value_str,type_str)

        # Proceed if the value obtained in the appropriated type 
        valid = valid_type
        if(valid):
            # If the list of option is not empty
            if(options):
                # If the value is not on the list
                if(not value in options):
                    # Invalidate the value
                    valid = False
                    # Throw an error message if value is invalid (not on the provided list)
                    messagebox.showerror("Error", "Value inserted is not a valid option")

        return valid, value


    def saveas_json(self):
        """
        Function to save the current set os parameters as a new file
        """

        # Open a file dialog to select a path ans set a name for the new file to be saved
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        # If a path and a name were provided
        if path:
            # Set the new path
            self.file_path = path
            # Save current set of parameters as a JSON file
            self.save_json()


    def save_json(self):
        """
        Function to dump the current set os parameters to the origin JSON file
        """

        try:
            # If path is set
            if self.file_path:
                # Open the file
                with open(self.file_path, "w") as json_file:
                    # Dump the parameters data to the file
                    json.dump(self.data, json_file, indent=4)
        except:
            # Throw an error message there was a problem in saving the file
            messagebox.showerror("Error", "A problem ocurred when saving the file")


    def set_value(self):
        """
        Function to set the parameter on the entrybox/dropdown and update it on the tree
        """

        # Get the selected lines on the treeview
        selected_items = self.tree.selection()
        # If at least a line is selected
        if selected_items:
            # Get the first line selected
            selected_item = self.tree.selection()[0]
            # Get the name of the parameter
            selected_param = self.tree.item(selected_item, "text")
            # Get the inserted value for the parameter
            value_candidate = self.combobox.get()
            # Check if the candidate value is valid
            valid, new_value = self.check_value(value_candidate,self.data[selected_param]['type'],self.data[selected_param]['options'])
            # Ignore if the candidate is not valid
            if(not valid):
                return

            # Set the value if it was validated
            self.data[selected_param]['value'] = new_value

            # Set the color of the treeview line according if the current value is the default or not
            if new_value == self.data[selected_param]["default"]:
                # Set white color if parameter has the default value
                self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("white",))
            else:
                # Set orange color if parameter does not have the default value
                self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("orange",))

            # If autosave checkbox is selected
            if(self.auto_save()):
                # Save change to file
                self.save_json()


    def set_default_value(self):
        """
        Function to set the parameter on the entrybox/dropdown and update it on the tree
        """

        # Get the list of selected lines on the treeview
        selected_items = self.tree.selection()

        # For each selected line
        for selected_item in selected_items:
            # Get the name of the parameter
            selected_param = self.tree.item(selected_item, "text")
            # Get the default value of the selected parameter
            new_value = self.data[selected_param]['default']
            # Set the value to the default value
            self.data[selected_param]['value'] = new_value
            # Update the entry box with the new (default) value
            self.combobox.delete(0, tk.END)
            self.combobox.insert(0, str(new_value))
            self.combobox['values'] = self.data[selected_param]['options']
            # Update the treeview with the default value
            self.tree.item(selected_item, values=(new_value, self.data[selected_param]['unit'], self.data[selected_param]['description'].split('\n')[0]), tags=("white",))

        # If autosave checkbox is selected and there was at least one line selected
        if(self.auto_save() and selected_items):
            # Save change to file
            self.save_json()


    def auto_save(self):
        """
        Function that returns if the autosave checkbox is checked or not

        Return:
            (bool): State of the autosave checkbox
        """
        return self.checkbox_state.get()


if __name__ == "__main__":
    """
    Main to run a detached JsonEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='radiance') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Parameters Editor")
    # Define GUI window size
    root.geometry('1150x500')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/params_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = JsonEditorGUI(root, True)

    # Run the tkinter event loop
    root.mainloop()

