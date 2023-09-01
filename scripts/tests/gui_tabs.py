#!/usr/bin/env python3
# -*- coding:utf-8 -*-



import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from ttkthemes import ThemedTk



# Global variable to store the number from Inner Tab 2
saved_number = None

# Function for Inner Tab 1 button
def display_message():
    messagebox.showinfo("Message", "Hello from GUI")

# Function for Inner Tab 2 button
def save_number():
    global saved_number
    try:
        number = float(entry.get())
        saved_number = number
        messagebox.showinfo("Success", "Number saved successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid number format!")

# Function for Inner Tab 3 button
def display_saved_number():
    global saved_number
    if saved_number is not None:
        messagebox.showinfo("Saved Number", f"The saved number is: {saved_number}")
    else:
        messagebox.showerror("Error", "No number saved yet!")

# Create the main window
# root = tk.Tk()
# root.title("Custom Copter Simulator")
# themes = ['clam', 'alt', 'default', 'classic']
# ttk.Style(root).theme_use(themes[0])

themes_list = ['scidpink', 'alt', 'itft1', 'classic', 'adapta', 'elegance', 'default', 'scidgrey', 'winxpblue', 'arc', 'scidmint', 'kroc', 'ubuntu', 'plastik', 'breeze', 'radiance', 'black', 'scidpurple', 'scidgreen', 'keramik', 'scidblue', 'equilux', 'aquativo', 'clam', 'scidsand', 'blue', 'clearlooks', 'smog', 'yaru']
# root = ThemedTk(theme="adapta")

# i = 28
# root = ThemedTk(theme=themes_list[i])
root = ThemedTk(theme='black')
root.title("Custom Copter Simulator")

# blue
# equilux
# scidblue
# scidgreen
# scidpurple - good
# black
# kroc - this is orange
# radiance
# breeze


# adapta - ok
# aquativo - good
# arc
# blue
# clearlooks
# elegance
# equilux
# itft1 - ok
# keramik
# plastik - ok
# radiance - good
# scidblue - ok
# smog
# winxpblue - ok
# winnative - ok

# Create the top-level notebook
top_notebook = ttk.Notebook(root)
top_notebook.pack(fill='both', expand=True)

# Create the first tab in the top-level notebook
tab1 = ttk.Frame(top_notebook)
top_notebook.add(tab1, text="Simulation")

# Create the second tab in the top-level notebook
tab2 = ttk.Frame(top_notebook)
top_notebook.add(tab2, text="Configuration")

# Create a second-level notebook inside Tab 2
second_level_notebook = ttk.Notebook(tab2)
second_level_notebook.pack(fill='both', expand=True)

# Create tabs inside the second-level notebook
inner_tab1 = ttk.Frame(second_level_notebook)
second_level_notebook.add(inner_tab1, text="Geolocation")

inner_tab2 = ttk.Frame(second_level_notebook)
second_level_notebook.add(inner_tab2, text="Sensors")

inner_tab3 = ttk.Frame(second_level_notebook)
second_level_notebook.add(inner_tab3, text="Full Parameter Set")

# Populate the inner tabs with content
# Inner Tab 1
button1 = ttk.Button(inner_tab1, text="Display Message", command=display_message)
button1.pack(padx=20, pady=20)

# Inner Tab 2
entry = ttk.Entry(inner_tab2)
entry.pack(padx=20, pady=10)

button2 = ttk.Button(inner_tab2, text="Save Number", command=save_number)
button2.pack(padx=20, pady=10)

# Inner Tab 3
button3 = ttk.Button(inner_tab3, text="Display Saved Number", command=display_saved_number)
button3.pack(padx=20, pady=20)

# Start the Tkinter main loop
root.mainloop()














# import tkinter as tk
# from tkinter import ttk

# # Create the main window
# root = tk.Tk()
# root.title("Nested Tabs Example")

# # Create the top-level notebook
# top_notebook = ttk.Notebook(root)
# top_notebook.pack(fill='both', expand=True)

# # Create the first tab in the top-level notebook
# tab1 = ttk.Frame(top_notebook)
# top_notebook.add(tab1, text="Tab 1")

# # Create the second tab in the top-level notebook
# tab2 = ttk.Frame(top_notebook)
# top_notebook.add(tab2, text="Tab 2")

# # Create a second-level notebook inside Tab 2
# second_level_notebook = ttk.Notebook(tab2)
# second_level_notebook.pack(fill='both', expand=True)

# # Create tabs inside the second-level notebook
# inner_tab1 = ttk.Frame(second_level_notebook)
# second_level_notebook.add(inner_tab1, text="Inner Tab 1")

# inner_tab2 = ttk.Frame(second_level_notebook)
# second_level_notebook.add(inner_tab2, text="Inner Tab 2")

# inner_tab3 = ttk.Frame(second_level_notebook)
# second_level_notebook.add(inner_tab3, text="Inner Tab 3")

# # Populate the inner tabs with content (labels in this example)
# label1 = ttk.Label(tab1, text="Content for Tab 1")
# label1.pack(padx=20, pady=20)

# label2 = ttk.Label(tab2, text="Content for Tab 2")
# label2.pack(padx=20, pady=20)

# label3 = ttk.Label(inner_tab1, text="Content for Inner Tab 1")
# label3.pack(padx=20, pady=20)

# label4 = ttk.Label(inner_tab2, text="Content for Inner Tab 2")
# label4.pack(padx=20, pady=20)

# label5 = ttk.Label(inner_tab3, text="Content for Inner Tab 3")
# label5.pack(padx=20, pady=20)

# # Start the Tkinter main loop
# root.mainloop()










# import tkinter as tk
# from tkinter import ttk

# def create_tab1():
#     tab1 = ttk.Frame(notebook)
#     notebook.add(tab1, text="Home")
#     label1 = ttk.Label(tab1, text="This is Tab 1")
#     label1.pack(padx=20, pady=20)

# def create_tab2():
#     tab2 = ttk.Frame(notebook)
#     notebook.add(tab2, text="Config")
#     label2 = ttk.Label(tab2, text="This is Tab 2")
#     label2.pack(padx=20, pady=20)

# def create_tab3():
#     tab3 = ttk.Frame(notebook)
#     notebook.add(tab3, text="Tab 3")
#     label3 = ttk.Label(tab3, text="This is Tab 3")
#     label3.pack(padx=20, pady=20)

# # Create the main window
# root = tk.Tk()
# root.title("Tabbed GUI")

# # Create a Notebook widget to manage tabs
# notebook = ttk.Notebook(root)
# notebook.pack(fill='both', expand=True)

# # Create tabs
# create_tab1()
# create_tab2()
# create_tab3()

# # Start the Tkinter main loop
# root.mainloop()

