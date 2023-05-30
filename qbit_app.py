import sys
import numpy as np
# serial monitor communication
from serial import Serial
#pyqt6 modules
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit, QDialog, QPushButton, QGridLayout
# mean for averages
from statistics import mean
# imports for matplotlib
from matplotlib.figure import Figure
from matplotlib.backends import backend_qt5agg

# imports for tkinter
import numpy as np
from tkinter import *
import customtkinter as ctk

# CTK app settings - 
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


# create working thread to run arduino read in the backround
# prevents the gui from freezing
class WorkerThread(QThread):
    def __init__(self, mainwindow):
        super().__init__()

        # this is what is 'hack-y'. passing the mainwindow class into the thread class so i can run the set_values function from this class
        self.main_window = mainwindow

        # opening serial monitor, happens only once on initialization
        self.open_serial_monitor()

        # intializes list that will save the values and resets it everytime a new reading is taken
        self.value_list = []


    # running the read_arduino function in the Arduino_Read cass. runs continuously, serial monitor opened once and stays open
    def run(self):
        # get values and store them in a list
        self.read_arduino()

    
    # opens the serial monitor
    def open_serial_monitor(self):
        # indicates that serial monitor has been opened
        print('serial monitor opened')

        # intitializes the access to the serial port
        self.ser = Serial()
        
        # specifies which serial port
        portVar = '/dev/cu.usbmodem1202'
        
        # opening serial port
        self.ser.baudrate = 9600
        self.ser.port = portVar
        self.ser.open()


    # takes in readings from the arduino and averages 10. emits a signal with the averages when the new ones are calculated
    def read_arduino(self):
        # while the arduino is running
        while True:
            if self.ser.in_waiting:
                packet = self.ser.readline()

                # add to the list until it has 10 readings
                if len(self.value_list)<10:
                    # take the set of 7 values
                    value_string = packet.decode('utf').rstrip('\n')

                    # if good read, add the values to the value set
                    try:
                        value_set = [float(item.strip()) for item in value_string.split(',')]

                        # add each set of values to the list to be averaged
                        self.value_list.append(value_set)

                    # if a bad read, print bad read
                    except:
                        print('bad read')
                        pass


                # if at 10 readings, take the averages and return the result
                else:
                    # further filtering to remove any readings that don't consist of 7 values
                    for i, item in enumerate(self.value_list):
                        if len(item) < 8:
                            self.value_list.pop(i)

                    # iterate through the value list and make an an idividual list for the readings of each variable
                    averages = []
                    for sublist in self.value_list:
                        sublist_averages = []
                        for i in range(7):
                            values = [sublist[i]]
                            avg = round(mean(values)/10, 2)
                            sublist_averages.append(avg)
                        averages.extend(sublist_averages)

                    self.main_window.set_values(averages)
                    self.value_list = []



# main window of the gui
class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        # window visuals
        self.width = 1000 # 2:1 Width:Height Aspect Ratio Used
        self.height = 700
        self.title("Ultraportable ECMO Data Visualization App")
        self.iconbitmap("Caduceus_icon_gold.ico")
        self.geometry(f"{self.width}x{self.height}")
        self.minsize(self.width, self.height)

        # setting protocal
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # creating fonts for use in the window
        self.fontData = ctk.CTkFont(family="Helvetica", size=12, weight="bold")
        self.fontTitle = ctk.CTkFont(family="Roboto Medium", size=16)
        self.fontAuthors = ctk.CTkFont(family="Roboto Medium", size=10)

        # other part of the 'hack-y' fix. creates an instance of the WorkerThread, passing in itself so that its functions can be accessed by the thread
        self.thread = WorkerThread(self)

        # need to configure matplotlib plots

        # call function to create all the gui visuals
        self.gui_visuals()

        # starting thread that reads the arduino values
        self.run_thread()

        # set the created layout as the layout for the app


    # functon that creates all the visuals for the gui, this is where changes would be made for the layout
    # new functions will be needed for buttons etc that change the layout depending on what is selected
    def gui_visuals(self):
        # making the 2 main frames, one for plots one for readings
        # configure grid layout (1x2) (row x col)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # create the left and right frames
        self.left_frame()
        self.right_frame()
        self.setting_frame()

        # authorship Statement
        self.authors_Label = ctk.CTkLabel(master=self.frame_left, text="Created by Daniel Kurtz and Alina Gammage for QBiT", font=self.fontAuthors)
        self.authors_Label.grid(row=13, column=1, pady=20, padx=20,sticky="ew")


    # make left frame
    def left_frame(self):
        # left frame
        self.frame_left = ctk.CTkFrame(master=self, width=315, corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe", padx=20, pady=20)
        self.frame_left.grid_propagate(False)
        # title
        self.title_Label = ctk.CTkLabel(master=self.frame_left, text="Ultraportable ECMO DataVis", font=self.fontTitle)
        self.title_Label.grid(row=1, column=1, pady=10, padx=10)
        # configure Grid Layout (15x3)
        self.frame_left.grid_rowconfigure(0, minsize=10)
        self.frame_left.grid_rowconfigure(2, minsize=10)
        self.frame_left.grid_rowconfigure(4, minsize=5)
        self.frame_left.grid_rowconfigure(6, minsize=5)
        self.frame_left.grid_rowconfigure(8, minsize=5)
        self.frame_left.grid_rowconfigure(10, minsize=5)
        self.frame_left.grid_rowconfigure(12, minsize=10)
        self.frame_left.grid_rowconfigure(14, minsize=10)
        self.frame_left.grid_columnconfigure(0, minsize=10)
        self.frame_left.grid_columnconfigure(2, minsize=10) 

        # creating all the visuals for the readings in the left frame
        self.left_frame_reads()

    def left_frame_reads(self):
        self.read_types = ['Blood Pressure', 'Outlet Temperature', 'Flowrate', 'Oxygen Concentration', 'Carbon Dioxide Concentration']
        self.labels = {}
        self.read = {}
        self.frame = {}
        self.array = {}
        self.new_read_value = {}

        # putting values in dictionaries
        row = 3
        for read_type in self.read_types:
            self.labels[read_type], self.read[read_type], self.frame[read_type], self.array[read_type], self.new_read_value[read_type] = self.make_visuals(read_type, row)
            row += 2


    # make right frame
    def right_frame(self):
        # entire right frame
        # configure frame
        self.frame_right = ctk.CTkFrame(master=self, width=700, bg_color= '#969696', fg_color= '#969696')
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)
        self.frame_right.grid_propagate(False)
        # configure grid layout (5x4)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(1, weight=1)
        self.frame_right.grid_columnconfigure(2, weight=1)
        self.frame_right.grid_columnconfigure(3, weight=1)
        self.frame_right.grid_rowconfigure(0, weight=10)
        self.frame_right.grid_rowconfigure(2, weight=10)
        self.frame_right.grid_rowconfigure(4, weight=1)

        # blood pressures plot
        #configure frame
        self.frameR_left_top = ctk.CTkFrame(master=self.frame_right)
        self.frameR_left_top.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew")
        self.frameR_left_top.configure(border_width=2, border_color='#969696', corner_radius=0)
        # configure grid layout (1x1)
        self.frameR_left_top.rowconfigure(0, weight=1)
        self.frameR_left_top.columnconfigure(0, weight=1)
        self.label_R_LT = ctk.CTkLabel(master=self.frameR_left_top, text="Blood Pressures", font=self.fontTitle)
        self.label_R_LT.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)

        # flow rate plot
        # configure frame
        self.frameR_right_top = ctk.CTkFrame(master=self.frame_right)
        self.frameR_right_top.grid(row=0, column=2, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_right_top.configure(border_width=2, border_color='#969696', corner_radius=0)
        # configure grid layout (1x1)
        self.frameR_right_top.rowconfigure(0, weight=1)
        self.frameR_right_top.columnconfigure(0, weight=1)
        self.label_R_RT = ctk.CTkLabel(master=self.frameR_right_top, text="Flow Rate", font=self.fontTitle)
        self.label_R_RT.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)

        # blood O2 plot
        # configure frame
        self.frameR_left_bot = ctk.CTkFrame(master=self.frame_right)
        self.frameR_left_bot.grid(row=2, column=0, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_left_bot.configure(border_width=2, border_color='#969696',  corner_radius=0)
        # configure grid layout (1x1)
        self.frameR_left_bot.rowconfigure(0, weight=1)
        self.frameR_left_bot.columnconfigure(0, weight=1)
        self.label_R_LB = ctk.CTkLabel(master=self.frameR_left_bot, text="Blood [O2]", font=self.fontTitle)
        self.label_R_LB.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)
        
        # blood co2 plot
        # configure frame
        self.frameR_right_bot = ctk.CTkFrame(master=self.frame_right)
        self.frameR_right_bot.grid(row=2, column=2, columnspan=2, rowspan=2, sticky="nswe")
        self.frameR_right_bot.configure(border_width=2, border_color='#969696', corner_radius=0)
        # configure grid layout (1x1)
        self.frameR_right_bot.rowconfigure(0, weight=1)
        self.frameR_right_bot.columnconfigure(0, weight=1)
        self.label_R_RB = ctk.CTkLabel(master=self.frameR_right_bot, text="Blood [CO2]", font=self.fontTitle)
        self.label_R_RB.grid(column=0, row=0, sticky="nswe", padx=15, pady=15)
    
    def setting_frame(self):
        self.frameSettings = ctk.CTkFrame(master=self.frame_right)
        self.frameSettings.grid(row=4, column=0, columnspan=4, rowspan=1, sticky="nswe")
        self.frameSettings.configure(border_width=2, border_color='#969696', corner_radius=0)

        entry_option = ctk.StringVar(value="Conditions")

        self.value_option_menu = ctk.CTkOptionMenu(master=self.frameSettings, values=["Conditions", "Blood Outlet T",  "Blood Flow Rate", "Blood [O2]", "Blood [CO2]"], command = self.value_selection_menu_callback, variable = entry_option)
        self.value_option_menu.grid(row=0, column=0, columnspan = 4, padx=20, pady=(20, 10))
        self.string_input_button = ctk.CTkButton(master=self.frameSettings, text="Input a Value", command=self.open_input_dialog_event)
        self.string_input_button.grid(row=1, column=0, padx=20, pady=(10, 10))


        # making array 1 to 100 for time
        self.time = [0]
        self.timer = 0
 

    # function that runs the thread, called once when the pop up is closed
    def run_thread(self):
        # start the thread
        self.thread.start()


    # called by the thread with the list of new averages to be displayed
    def set_values(self, val_list):
        if self.timer > 100:
            self.time = [0]
            self.timer = 0
            for read_type in self.read_types:
                self.array[read_type] = []
        # displaying new reads
        for i, read_type in enumerate(self.read_types):
            self.new_read_value[read_type] = val_list[i]
            self.read[read_type].configure(text=(str(val_list[i])))
        # # updating plots
        # for read_plot in self.read_plots:
        #     if read_plot == 'Blood Pressure':
        #         self.update_plot(read_plot, self.new_read_value['Diastolic Blood Pressure'], self.new_read_value['Systolic Blood Pressure'])
        #     else:
        #         self.update_plot(read_plot, self.new_read_value[read_plot])
            # update timer
        self.timer += 1
        self.time.append(self.timer)


    # makes the visuals
    def make_visuals(self, title, row):
        frame = ctk.CTkFrame(master=self.frame_left)
        frame.grid(row=row, column=1, columnspan=1, rowspan=1, sticky = "nswe")
        frame.grid_rowconfigure(0, minsize=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        label = ctk.CTkLabel(master=frame, text=title, font=self.fontData)
        label.grid(row=1, column=0, padx=10)
        read_label = ctk.CTkLabel(master=frame, text='-', font=self.fontData)
        read_label.grid(row=2, column=0, padx=10)
        read_label.grid_rowconfigure(3, minsize=5)
        value_array = []
        new_read = 0

        # returns the visual objects
        return label, read_label, frame, value_array, new_read
    
    # make the plots
    def make_plots(self, title):
        # create a Figure object and add a subplot
        figure = Figure() 
        canvas = self.figure_canvas(figure)
        axes = figure.add_subplot(111)
        axes.set_xlim(0, 100)
        axes.set_ylim(0, 10)

        return axes, canvas

    def update_plot(self, plot_read, new_value1, new_value2=None):
        # update two values on the same plot if it's the blood pressure
        self.plots[plot_read].clear()
        if plot_read == 'Blood Pressure':
            self.array['Diastolic Blood Pressure'].append(new_value1)
            self.array['Systolic Blood Pressure'].append(new_value2)
            self.plots['Blood Pressure'].plot(self.time, self.array['Diastolic Blood Pressure'])
            self.plots['Blood Pressure'].plot(self.time, self.array['Systolic Blood Pressure'])
    # update only the one value if it isn't blood pressure
        else:
            self.array[plot_read].append(new_value1)
            self.plots[plot_read].plot(self.time, self.array[plot_read])

        # update the plot
        self.plots[plot_read].set_xlim(0, 100)
        self.plots[plot_read].set_ylim(0, 10)
        self.canvas[plot_read].draw()

    # close the application
    def on_closing(self, event=0):
        self.destroy()

    # start the application
    def start(self):
        self.mainloop()

    # value selection
    def value_selection_menu_callback(self, entry_option):
        print("Selected:", entry_option)

    # value entry box
    def open_input_dialog_event(self):
        dialog = ctk.CTkInputDialog(text="Type in the desired " + self.value_option_menu.get(), title="Value Input Window")
        user_input_value = str(dialog.get_input())
        print(user_input_value)


# run the application
if __name__ == "__main__":
    app = MainWindow()
    app.start()
    print('showing window')