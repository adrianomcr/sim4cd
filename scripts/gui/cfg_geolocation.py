#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to configure the geographic properties properties

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from ttkthemes import ThemedTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image
from math import pi, sin, cos, asin, sqrt, atan2

import poly_estimator as PEST


class GeolocationEditorGUI:
    """
    Class that defines a GUI for configuring the actuators properties
    """

    def __init__(self, root_, enable_io_=True):
        """
        Constructor for the GeolocationEditorGUI class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
            enable_io_ (bool): Flag to enable the creation of input/output buttons to the gui
        """

        # Set the root variable
        self.root = root_

        # Set the io_enabled variable
        self.io_enabled = enable_io_

        # Define a left panel
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill="both", expand=False)
        # Add a title for the left panel
        self.name_l_label = ttk.Label(self.left_frame, text="Geolocation configuration")
        self.name_l_label.pack(padx=5)

        # Define a right panel
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side=tk.LEFT, fill="both", expand=True)
        # Add a title for the right panel
        self.name_r_label = ttk.Label(self.right_frame, text="Global position")
        self.name_r_label.pack(padx=5)

        if(self.io_enabled):
            # Create buttons to load and save file
            buttons_frame = ttk.Frame(self.left_frame)
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

        # Initialize the variable to store the json path
        self.file_path = False
        
        # Initialize the variable to store the json data
        self.data = {}

        # Read the map image
        self.bm = Image.open(os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/earthicefree.jpg')
        # Create separate images for R, G and B with values from 0 to 1
        self.r, self.g, self.b = self.bm.split()
        self.r = np.array(self.r)/256.0
        self.g = np.array(self.g)/256.0
        self.b = np.array(self.b)/256.0
        # Compute the size of the image
        self.W, self.H = self.bm.size

        # Build the left and right panels
        self.build_left_panel()
        self.build_right_panel()

        # Update the Earth plot
        self.update_earth_image(0,0)


    def build_left_panel(self):
        """
        Function to build the widgets into the left panel
        """

        # Create a subframe for geografic origin properties
        geographic_label = ttk.Label(self.left_frame, text="Geolocation")
        geographic_label.pack(side=tk.TOP, pady=(20,2))
        geographic_frame = ttk.Frame(self.left_frame)
        geographic_frame.pack(side=tk.TOP, pady=(2,20))
        # Add label, entry and units for origin latitude
        lat_label = ttk.Label(geographic_frame, text="  Latitude")
        lat_label.grid(row=0, column=0)
        self.combo_lat = ttk.Combobox(geographic_frame, values=[])
        self.combo_lat.grid(row=0, column=1)
        lat_unit_label = ttk.Label(geographic_frame, text="[degrees]")
        lat_unit_label.grid(row=0, column=2)
        # Add label, entry and units for origin longitude
        lon_label = ttk.Label(geographic_frame, text="Longitude")
        lon_label.grid(row=1, column=0)
        self.combo_lon = ttk.Combobox(geographic_frame, values=[])
        self.combo_lon.grid(row=1, column=1)
        lon_unit_label = ttk.Label(geographic_frame, text="[degrees]")
        lon_unit_label.grid(row=1, column=2)
        # Add label, entry and units for origin altitude
        alt_label = ttk.Label(geographic_frame, text="  Altitude")
        alt_label.grid(row=2, column=0)
        self.combo_alt = ttk.Combobox(geographic_frame, values=[])
        self.combo_alt.grid(row=2, column=1)
        alt_unit_label = ttk.Label(geographic_frame, text="[meters]")
        alt_unit_label.grid(row=2, column=2)        

        # Create a subframe for local magnetic field properties
        magnetic_label = ttk.Label(self.left_frame, text="Local magnetic field")
        magnetic_label.pack(side=tk.TOP, pady=(10,2))
        magnetic_frame = ttk.Frame(self.left_frame)
        magnetic_frame.pack(side=tk.TOP, pady=(2,20))
        # Add label, entry and units for local magnetic field pointinh East
        mag_east_label = ttk.Label(magnetic_frame, text="   East")
        mag_east_label.grid(row=0, column=0)
        self.combo_mag_east = ttk.Combobox(magnetic_frame, values=[])
        self.combo_mag_east.grid(row=0, column=1)
        mag_east_unit_label = ttk.Label(magnetic_frame, text="[Gauss]")
        mag_east_unit_label.grid(row=0, column=2)
        # Add label, entry and units for local magnetic field pointinh North
        mag_north_label = ttk.Label(magnetic_frame, text=" North")
        mag_north_label.grid(row=1, column=0)
        self.combo_mag_north = ttk.Combobox(magnetic_frame, values=[])
        self.combo_mag_north.grid(row=1, column=1)
        mag_north_unit_label = ttk.Label(magnetic_frame, text="[Gauss]")
        mag_north_unit_label.grid(row=1, column=2)
        # Add label, entry and units for local magnetic field pointinh up
        mag_up_label = ttk.Label(magnetic_frame, text="     Up")
        mag_up_label.grid(row=2, column=0)
        self.combo_mag_up = ttk.Combobox(magnetic_frame, values=[])
        self.combo_mag_up.grid(row=2, column=1)
        mag_up_unit_label = ttk.Label(magnetic_frame, text="[Gauss]")
        mag_up_unit_label.grid(row=2, column=2)

        # Add button to apply the estimated coefficients to the current actuator
        self.set_button = ttk.Button(self.left_frame, text="Set values", padding=(4, 4), command=self.set_values)
        self.set_button.pack(pady=2, side=tk.TOP)

        # TODO
        tmp_label = ttk.Label(self.left_frame, text="\nAdd mag field computator\nInternet?\nPython?")
        tmp_label.pack()

        # Bind the set function to the the enter key
        self.combo_lat.bind("<Return>", lambda event=None: self.set_values())
        self.combo_lon.bind("<Return>", lambda event=None: self.set_values())
        self.combo_alt.bind("<Return>", lambda event=None: self.set_values())
        self.combo_mag_east.bind("<Return>", lambda event=None: self.set_values())
        self.combo_mag_north.bind("<Return>", lambda event=None: self.set_values())
        self.combo_mag_up.bind("<Return>", lambda event=None: self.set_values())


    def build_right_panel(self):
        """
        Function to build the widgets into the right panel
        """

        # Create a pyplot figure
        self.fig, self.axs = plt.subplots(1,1)
        # Set a background color
        self.fig.set_facecolor('#101010')

        # Create a canvas for the plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # Update the plot
        self.canvas.draw()
        # Attach the plot to the right_frame
        self.canvas.get_tk_widget().pack()


    def rad_to_id(self,lat,lon):
        """
        Compute the latitude and longitude of a point in the surface of a unit sphere

        Parameters:
            lat (float): Latitude in radians
            lon (float): Longitude in radians

        Returns:
            lat_id (int): Index of the latitude in the map image
            lon_id (int): Index of the longitude in the map image
        """

        # Compute indexes    
        lat_id = int( -(self.H-1)*(lat/pi-0.5) )
        lon_id = int( (self.W-1)*(lon/(2*pi)+0.5) )
        return lat_id, lon_id


    def point_to_latlon(self,p):
        """
        Compute the latitude and longitude of a point in the surface of a unit sphere

        Parameters:
            p (numpy.ndarray): Point of unit norm

        Returns:
            lat (float): Latitude correspondent to the point p in radians
            lon (float): Longitude correspondent to the point p in radians
        """

        # Compute longitude
        lon = atan2(p[1],p[0])
        # Compute latitude
        lat = asin(p[2]*0.999999999)
        return lat,lon


    def update_earth_image(self,lat0,lon0):
        """
        Update the plot of the Earth showing the current geolocation

        Parameters:
            lat0 (float): Origin latitude in radians
            lat0 (float): Origin longitude in radians
        """

        # Size of the image
        L = 300
        # Black margin of the image
        M = 20

        # Create  black image of size (LxL)
        P = [[[0 for i in range(L+2*M)] for j in range(L+2*M)] for d in range(3)]

        # Compute the Earth image if there is data available
        if(self.file_path):

            # Rotation around z representing longitude
            Rz = np.array([[cos(lon0), -sin(lon0), 0],
                        [sin(lon0), cos(lon0) , 0],
                        [0        , 0         , 1]])
            # Rotation around y representing latitude
            Ry = np.array([[cos(-lat0) ,  0, sin(-lat0)],
                        [0         ,  1, 0],
                        [-sin(-lat0),  0, cos(-lat0)]])

            # Compute the rotation of a plane in which the Earth surface wil be projected
            R_p_w =Rz@Ry

            # Compute vectors to span a projected image in the scale from -1 t0 1
            y_vec = [ 2*i/L-1 for i in range(L+1)]
            z_vec = [ -(2*i/L-1) for i in range(L+1)]
            # Iterate over the pixels of the image
            for i, y in enumerate(y_vec):
                for j, z in enumerate(z_vec):
                    # If thee is a point in earth surface that projects to the current pixel (is inside a unit circle)
                    if(y**2+z**2<1):
                        # Compute the x coordinate of the 
                        x = sqrt(1 - y**2 - z**2)
                        # Compute the point in the Earth surface (sphere of radius 1)
                        point_p = np.array([x,y,z])   # In the local frame defined by (lat,lon)=(lat0,lon0)
                        point_w = R_p_w.dot(point_p)  # In the Earth frame (lat,lon)=(0,0)

                        # Compute the (lat,lon) associated to the point point_w
                        lat,lon = self.point_to_latlon(point_w)
                        # Compute the pixel of the map image that represents the (lat,lon)
                        lat_id, lon_id = self.rad_to_id(lat,lon)

                        # Set the image P with the correct pixel of the map
                        P[0][j+M][i+M] = self.r[lat_id,lon_id]
                        P[1][j+M][i+M] = self.g[lat_id,lon_id]
                        P[2][j+M][i+M] = self.b[lat_id,lon_id]

        # Create an RGB image
        color_image = np.stack((np.array(P[0][:][:]),np.array(P[1][:][:]),np.array(P[2][:][:])), axis=-1)
        # Clear the plot
        self.axs.clear()
        # Show the image (black image if there is no data)
        self.axs.imshow(color_image)

        # If there is data available
        if(self.file_path):
            # Plot a red point at (lat,lon)=(lat0,lon0)
            self.axs.scatter(L/2+M, L/2+M, color='red', s=20)
            # Compute a circle
            circ_x = [(L+2*M)/2+((L+1)/2)*cos(2*pi*k/999) for k in range(1000)]
            circ_y = [(L+2*M)/2+((L+1)/2)*sin(2*pi*k/999) for k in range(1000)]
            # plot a circle representing the Earth atmosphere
            self.axs.plot(circ_x, circ_y, color='cyan',linewidth=2)

        # Set the scale of the image
        plt.xlim(-1,L+2*M)
        plt.ylim(L+2*M,-1)
        # Remove the axis
        self.axs.axis('off')

        # Show the plot and proceed
        self.canvas.draw()


    def set_values(self):
        """
        Function to set the values inserted in the gui to the data dictionary
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            messagebox.showerror("Error", "There is no parameter file loaded")
            return

        # Set geolocation properties inserted on the gui to the data dictionary
        self.data["SENS_LAT_ORIGIN"]['value'] = float(self.combo_lat.get())
        self.data["SENS_LON_ORIGIN"]['value'] = float(self.combo_lon.get())
        self.data["SENS_ALT_ORIGIN"]['value'] = float(self.combo_alt.get())
        # Set local magnetic field properties inserted on the gui to the data dictionary
        self.data["SENS_MAG_FIELD_E"]['value'] = float(self.combo_mag_east.get())
        self.data["SENS_MAG_FIELD_N"]['value'] = float(self.combo_mag_north.get())
        self.data["SENS_MAG_FIELD_U"]['value'] = float(self.combo_mag_up.get())

        # Update data displayed on the gui displayed
        self.update_displayed_data()


    def update_displayed_data(self, *args):
        """
        Function to update the data displayed on the gui

        Parameters:
            *args (list): Unused arguments passed by the function when it is binded to a widget action.
        """

        # Return if there is parameter file loaded
        if(not self.file_path):
            return

        # Update the value of actuator time constant
        self.combo_lat.delete(0, tk.END)
        self.combo_lat.insert(0, str(self.data["SENS_LAT_ORIGIN"]['value']))
        self.combo_lat['values'] = self.data[f"SENS_LAT_ORIGIN"]['options']
        # Update the value of actuator moment of inertia
        self.combo_lon.delete(0, tk.END)
        self.combo_lon.insert(0, str(self.data[f"SENS_LON_ORIGIN"]['value']))
        self.combo_lon['values'] = self.data[f"SENS_LON_ORIGIN"]['options']
        # Update the value of actuator spin
        self.combo_alt.delete(0, tk.END)
        self.combo_alt.insert(0, str(self.data["SENS_ALT_ORIGIN"]['value']))
        self.combo_alt['values'] = self.data["SENS_ALT_ORIGIN"]['options']

        # Update the value of actuator time constant
        self.combo_mag_east.delete(0, tk.END)
        self.combo_mag_east.insert(0, str(self.data["SENS_MAG_FIELD_E"]['value']))
        self.combo_mag_east['values'] = self.data[f"SENS_MAG_FIELD_E"]['options']
        # Update the value of actuator moment of inertia
        self.combo_mag_north.delete(0, tk.END)
        self.combo_mag_north.insert(0, str(self.data[f"SENS_MAG_FIELD_N"]['value']))
        self.combo_mag_north['values'] = self.data[f"SENS_MAG_FIELD_N"]['options']
        # Update the value of actuator spin
        self.combo_mag_up.delete(0, tk.END)
        self.combo_mag_up.insert(0, str(self.data["SENS_MAG_FIELD_U"]['value']))
        self.combo_mag_up['values'] = self.data["SENS_MAG_FIELD_U"]['options']

        # Update the Earth plot showing the current geolocation
        lat0 = float(self.combo_lat.get())*pi/180
        lon0 = float(self.combo_lon.get())*pi/180
        self.update_earth_image(lat0,lon0)


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


    def load_json(self):
        """
        Function to show a file dialog to load a json file
        """
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if path:
            self.file_path = path
            with open(self.file_path, "r") as json_file:
                self.data = json.load(json_file)
            
            self.update_displayed_data()


    def on_closing(self):
        """
        Function to handle action when window is closed
        """
        # Close matplotlib.pyplot to avoid gui to keep alive after it is closed
        plt.close()


    def set_data(self, d, path):
        """
        Set data dictionary and the file path of the gui

        Parameters:
            d (dict): Updated dictionary with the parameters data edited in other guis
            path (str): path for the json file that stores the parameters
        """
        # Set data dictionary and file path
        self.data = d
        self.file_path = path

        # Update the gui with the new data
        self.update_displayed_data()


    def get_data(self):
        """
        Return the current data dictionary that the gui is using

        Return:
            self.data (dict): Dictionary with the parameters data edited on the gui
        """
        return self.data


    def viz_return(self):
        """
        Function to update the visualization of the gui
        """
        # Just call the update_displayed_data() function
        self.update_displayed_data()

 
if __name__ == "__main__":
    """
    Main to run a detached GeolocationEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Geolocation configuration")
    # Define GUI window size
    root.geometry('1200x600')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/geolocation_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = GeolocationEditorGUI(root, True)

    # Call the function to terminate the matplotlib.pyplot when window is closed
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Run the tkinter event loop
    root.mainloop()

