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
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # window visuals
        self.setWindowTitle('QBiT App Prototype')
        self.setStyleSheet('background-color: white')
        self.move(100,100)
        self.resize(1500, 500)

        # other part of the 'hack-y' fix. creates an instance of the WorkerThread, passing in itself so that its functions can be accessed by the thread
        self.thread = WorkerThread(self)

        # importing figure canvas to make a plot a widget
        self.figure_canvas = backend_qt5agg.FigureCanvasQTAgg

        # call function to create all the gui visuals
        self.gui_visuals()

        # starting thread that reads the arduino values
        self.run_thread()

        # set the created layout as the layout for the app
        widget = QWidget()
        widget.setLayout(self.full_layout)
        self.setCentralWidget(widget)


    # functon that creates all the visuals for the gui, this is where changes would be made for the layout
    # new functions will be needed for buttons etc that change the layout depending on what is selected
    def gui_visuals(self):
        # creating the layouts for the app
        self.labels_layout = QVBoxLayout()
        self.plot_grid = QGridLayout()
        self.full_layout = QHBoxLayout()

        # making the visual components for each of the read types
        # initializing dictionaries
        self.read_types = ['Inlet Temperature', 'Outlet Temperature', 'Systolic Blood Pressure', 'Diastolic Blood Pressure', 'Oxygen Concentration', 'Carbon Dioxide Concentration', 'Flowrate']
        self.read_plots = ['Blood Pressure', 'Oxygen Concentration', 'Carbon Dioxide Concentration', 'Flowrate']
        self.labels = {}
        self.read = {}
        self.vbox = {}
        self.array = {}
        self.plots = {}
        self.canvas = {}
        self.new_read_value = {}

        # putting values in dictionaries
        for read_type in self.read_types:
            self.labels[read_type], self.read[read_type], self.vbox[read_type], self.array[read_type], self.new_read_value[read_type] = self.make_visuals(read_type)
            self.vbox[read_type].addWidget(self.labels[read_type])
            self.vbox[read_type].addWidget(self.read[read_type])

        # putting the visual components into the app layout
            self.labels_layout.addLayout(self.vbox[read_type], 1)

        # creating each of the plots
        for read_plot in self.read_plots:
            self.plots[read_plot], self.canvas[read_plot] = self.make_plots(read_plot)
        
        # add each of the plots to the layout
        self.plot_grid.addWidget(self.canvas['Blood Pressure'], 1, 1)
        self.plot_grid.addWidget(self.canvas['Oxygen Concentration'], 1, 2)
        self.plot_grid.addWidget(self.canvas['Carbon Dioxide Concentration'], 2, 1)
        self.plot_grid.addWidget(self.canvas['Flowrate'], 2, 2)
        
        # adding the layouts to the main layout
        self.full_layout.addLayout(self.labels_layout)
        self.full_layout.addLayout(self.plot_grid)


        # making array 1 to 100 for time
        self.time = [0]
        self.timer = 0
 

    # function that runs the thread, called once when the pop up is closed
    def run_thread(self):
        # start the thread
        self.thread.start()


    # called by the thread with the list of new averages to be displayed
    def set_values(self, val_list):
        # displaying new reads
        for i, read_type in enumerate(self.read_types):
            self.new_read_value[read_type] = val_list[i]
            self.read[read_type].setText(str(val_list[i]))
        # updating plots
        for read_plot in self.read_plots:
            if read_plot == 'Blood Pressure':
                self.update_plot(read_plot, self.new_read_value['Diastolic Blood Pressure'], self.new_read_value['Systolic Blood Pressure'])
            else:
                self.update_plot(read_plot, self.new_read_value[read_plot])
            # update timer
        self.timer += 1
        self.time.append(self.timer)


    # makes the visuals
    def make_visuals(self,title):
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet('background-color: #7ba8f7')
        read = QLabel('-')
        read.setAlignment(Qt.AlignmentFlag.AlignCenter)
        read.setStyleSheet('background-color: #9d9ba2')
        vbox = QVBoxLayout()
        value_array = []
        new_read = 0
        # returns the visual objects
        return label, read, vbox, value_array, new_read
    
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
        if plot_read == 'Blood Pressure':
            self.array['Diastolic Blood Pressure'].append(new_value1)
            self.array['Systolic Blood Pressure'].append(new_value2)
            self.plots['Blood Pressure'].clear()
            self.plots['Blood Pressure'].plot(self.time, self.array['Diastolic Blood Pressure'])
            self.plots['Blood Pressure'].plot(self.time, self.array['Systolic Blood Pressure'])
       # update only the one value if it isn't blood pressure
        else:
            self.array[plot_read].append(new_value1)
            self.plots[plot_read].clear()
            self.plots[plot_read].plot(self.time, self.array[plot_read])

        # update the plot
        self.plots[plot_read].set_xlim(0, 100)
        self.plots[plot_read].set_ylim(0, 10)
        self.canvas[plot_read].draw()


# run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    print('showing window')
    window.show()
    sys.exit(app.exec())