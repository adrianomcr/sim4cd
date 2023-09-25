#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# GUI to perform polynomial identification

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from ttkthemes import ThemedTk
import os
import numpy as np

class PolyEstimatorGUI:
    """
    Class that defines a GUI to perform polynomial identification
    """

    def __init__(self, root_):
        """
        Constructor for the PolyEstimatorGUI class

        Parameters:
            root_ (tkinter.Tk): Object of the tkinter.Tk class where the TopazConfig gui will be built into
        """

        # Set the root variable
        self.root = root_
        # Initialize the coefficients variable and a existence flag
        self.C = None
        self.coefs_computed = False

        # Build the gui
        self.build_gui()


    def build_gui(self):
        """
        Function to build the widgets into the gui
        """

        # Create a main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill="both", expand=True)
        # Create a label with a title for the gui
        self.name_label = ttk.Label(self.main_frame, text="Polynomial estimator")
        self.name_label.pack(pady=2)

        # Create a treeview to display the points
        tree_scroll_frame = ttk.Frame(self.main_frame)
        tree_scroll_frame.pack(side=tk.TOP)
        self.tree = ttk.Treeview(tree_scroll_frame, columns=("X", "Y"), height=5)
        # Set the headers of each column
        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("#1", text=" X", anchor=tk.CENTER)
        self.tree.heading("#2", text="Y", anchor=tk.CENTER)
        # Configure the sizes of each column
        self.tree.column("#0", minwidth=1, width=1, stretch=tk.NO, anchor=tk.W)  # Column 0 (Name)
        self.tree.column("#1", minwidth=140, width=140, stretch=tk.YES, anchor=tk.CENTER)  # Column 1 (Value)
        self.tree.column("#2", minwidth=140, width=140, stretch=tk.YES, anchor=tk.CENTER)  # Column 1 (Value)
        # Pack the treeview
        self.tree.pack(side=tk.LEFT, fill="both", expand=True)
        # Define possible colors for the treeview lines
        self.tree.tag_configure("white", foreground="white")

        # Create a vertical scrollbar and attach it to the Treeview
        self.v_scrollbar = tk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.v_scrollbar.set)
        # Pack the scrollbar
        self.v_scrollbar.pack(side=tk.LEFT, fill="y")

        # Create a subframe for the entry boxes to intert the points
        self.point_entry_frame = ttk.Frame(self.main_frame)
        self.point_entry_frame.pack(side=tk.TOP, pady=5)
        # Create entry box for x
        self.x_entry = tk.Entry(self.point_entry_frame , width=15)
        self.x_entry.pack(padx=5, side=tk.LEFT, fill="x")
        # Create entry box for y
        self.y_entry = tk.Entry(self.point_entry_frame , width=15)
        self.y_entry.pack(padx=5, side=tk.LEFT, fill="x")

        # Create a subframe for buttons
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(side=tk.TOP, pady=5)
        # Create a button to add a point to the treeview
        self.add_button = ttk.Button(self.buttons_frame, text="    Add", padding=(3, 3), command=self.add_point)
        self.add_button.pack(padx=5, side=tk.LEFT)
        # Create a button to delete points from the treeview
        self.del_button = ttk.Button(self.buttons_frame, text="   Delete", padding=(3, 3), command=self.del_points)
        self.del_button.pack(padx=5, side=tk.LEFT)
        # Create a button to compute the coefficients
        self.compute_button = ttk.Button(self.buttons_frame, text=" Compute", padding=(3, 3), command=self.poly_identification)
        self.compute_button.pack(padx=5, side=tk.LEFT)

        # Add label to display the results
        self.coefs_label = ttk.Label(self.main_frame, text="")
        self.coefs_label.pack(pady=2, side=tk.TOP)


    def get_coefs(self):
        """
        Function to get the latest estimated coefficients

        Return:
            self.C (list of floats): List with the estimated coefficients
        """
        return self.C


    def has_coefs(self):
        """
        Function to return if there is an estimation available

        Return:
            self.coefs_computed (bool): True if there is a estimation available and False otherwise.
        """

        return self.coefs_computed


    def add_point(self):
        """
        Function to add the point in the entry boxes to the treeview
        """

        # Get the values in the entry boxes
        vx = self.x_entry.get()
        vy = self.y_entry.get()

        # Check if the entry boxes are not empty
        if (not (vx and vy)):
            messagebox.showerror("Error", "No number pair to add.")
            return

        try:
            # Add the values to the tree if they are numbers
            float(vx)
            float(vy)
            self.tree.insert("", "end", text='', values=(vx,vy), tags=("white",))
        except:
            # Display a error message if the values are not valid numbers
            messagebox.showerror("Error", "Invalid entry.\nMust be a number.")


    def del_points(self):
        """
        Function to delete selected points from the treeview
        """

        # Get the selected item(s)
        selected_items = self.tree.selection()

        # Ensure at leas one item is selected before attempting deletion
        if selected_items:
            # Delete the selected item(s)
            self.tree.delete(*selected_items)


    def poly_identification(self):
        """
        Function to estimate the polynomial based on the data in the treeview
        """

        # Initialize the data vectors
        xv = []
        yv = []

        # Inerate over the lines of the treeview and get the data
        count = 0
        for item in self.tree.get_children():
            count = count+1
            # Get the treeview line
            item_text = self.tree.item(item, "values")

            # Extract values of x and y ("y = poly(x)")
            x = float(self.tree.item(item, "value")[0])
            y = float(self.tree.item(item, "value")[1])
            # Store values in the vector
            xv.append(x)
            yv.append(y)


        if(count<3):
            # Do not execute the identification if there is not at least 3 points
            messagebox.showerror("Error", "Add at least 3 points")
            return
        else:
            # Define the matrices to compute the coefficients that the residual least squares
            A = []
            B = []
            for i in range(count):
                A.append([1.0, xv[i], xv[i]**2])
                B.append(yv[i])

            # Convert python lists to np.array
            A = np.array(A)
            B = np.array(B)

            try:
                # Try to compute the coefficients
                self.C = ( np.linalg.inv(A.transpose().dot(A)).dot(A.transpose()) ).dot(B) # C = inv(A'*A) * A'*B

                # Save that there is a estimation available
                self.coefs_computed = True
                # Display the result
                self.set_poly_text(self.C)
            except:
                # Display a error message if there was a problem in the computation of the polynomial coefficients
                # Likely caused by rank(A'*A) < 3
                messagebox.showerror("Error", "Error computing coefficients.\nCheck the input values.")


    def set_poly_text(self, c):
        """
        Function to create a string and display them written as a polynomial function

        Parameters:
            c (list of floats): List with the coefficients of the polynomial
        """

        rv = []
        sig = []
        for i, v in enumerate(c):
            # Round the value for display
            r = round(v*1000)/1000
            
            # Get the absolute values and the signals of each coefficient
            if r>=0:
                rv.append(str(abs(r)))
                if i>0:
                    sig.append(' + ')
                else:
                    sig.append(' ')
            else:
                rv.append(str(-r))
                sig.append(' - ')

        # Costruct the string
        s = 'p(u) ='+sig[0]+rv[0]+sig[1]+rv[1]+'*u'+sig[2]+rv[2]+'*u²'
        # Set the abel
        self.coefs_label.config(text=s)


if __name__ == "__main__":
    """
    Main to run a detached JsonEditorGUI window
    """

    # Define root GUI window
    root = ThemedTk(theme='black') #https://ttkthemes.readthedocs.io/en/latest/themes.html
    # Define GUI title
    root.title("Polynomial estimation")
    # Define GUI window size
    root.geometry('300x250')

    try:
        # Define and set a parameters icon for the GUI
        photo = tk.PhotoImage(file = os.path.abspath(__file__).rsplit('/', 1)[0]+'/resources/poly_est_icon.png')
        root.iconphoto(False, photo)
    except Exception as e:
        print("An error occurred while creating the icon:", e)

    # Create the GUI object
    app = PolyEstimatorGUI(root)

    # Run the tkinter event loop
    root.mainloop()

