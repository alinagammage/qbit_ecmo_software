import sys
# serial monitor communication
from serial import Serial
#pyqt6 modules
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit, QDialog, QPushButton
# mean for averages
from statistics import mean



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
        portVar = '/dev/cu.usbmodem11202'
        
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

    
    # prints to the serial monitor
    def print_to_monitor(self, value_dict):
        # writes the list to the serial monitor THIS LINE NOT WORKING
        self.ser.write(value_dict)



# main window of the gui
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # window visuals
        self.setWindowTitle('QBiT App Prototype')
        self.setStyleSheet('background-color: white')
        self.move(275, 100)
        self.resize(800, 100)

        # other part of the 'hack-y' fix. creates an instance of the WorkerThread, passing in itself so that its functions can be accessed by the thread
        self.thread = WorkerThread(self)

        # call function to create all the gui visuals
        self.gui_visuals()

        # create the list which hold the values in the text document
        self.temperature_input_value = 'ct' + str(0)
        self.flowrate_input_value = 'cf' + str(0)
        self.oxygen_input_value = 'co' + str(0)

        # creating the ok button for the pop up and connecting it to the close pop up function
        self.ok_button = QPushButton('ok')
        self.ok_button.pressed.connect(self.close_pop_up)
        self.defaults_pop_up()

        # set the created layout as the layout for the app
        widget = QWidget()
        widget.setLayout(self.hbox_layout)
        self.setCentralWidget(widget)


    # launch pop up
    def defaults_pop_up(self):
        # create pop up window, can change size etc
        self.pop_up = QDialog()
        self.pop_up.resize(100, 100)

        # pop up layout
        self.pop_up_vbox = QVBoxLayout()

        # make labels and input boxes
        temperature_default_label = QLabel('Set default temperature:')
        self.temperature_default = QLineEdit()
        flowrate_default_label = QLabel('Set default flowrate:')
        self.flowrate_default = QLineEdit()
        oxygen_default_label = QLabel('Set default blood oxygen concentration:')
        self.oxygen_default = QLineEdit()

        # add each of the labels and input boxes to layout
        self.pop_up_vbox.addWidget(temperature_default_label)
        self.pop_up_vbox.addWidget(self.temperature_default)
        self.pop_up_vbox.addWidget(flowrate_default_label)
        self.pop_up_vbox.addWidget(self.flowrate_default)
        self.pop_up_vbox.addWidget(oxygen_default_label)
        self.pop_up_vbox.addWidget(self.oxygen_default)
        self.pop_up_vbox.addWidget(self.ok_button)

        # launch pop up, launched first before the main gui
        self.pop_up.setLayout(self.pop_up_vbox)
        self.pop_up.exec()


    # function that closes the pop up. starts the thread and arduino readings.
    def close_pop_up(self):
        # actually close the pop up
        self.pop_up.close()

        # saving inputs
        self.temperature_input_default = str(self.temperature_default.text())
        self.flowrate_input_default = str(self.flowrate_default.text())
        self.oxygen_input_default = str(self.oxygen_default.text())

        # starts running the thread, opens the serial monitor
        self.run_thread()

        # writing inputs to serial monitor
        self.write_txt(self.temperature_input_default, None, None)
        self.write_txt(None, self.flowrate_input_default, None)
        self.write_txt(None, None, self.oxygen_input_default)



    # functon that creates all the visuals for the gui, this is where changes would be made for the layout
    # new functions will be needed for buttons etc that change the layout depending on what is selected
    def gui_visuals(self):
        # creating the layouts for the app
        self.hbox_layout = QHBoxLayout()
        self.full_layout = QVBoxLayout()

        # blood temp stuff
        # layout
        self.blood_temperature_vbox = QVBoxLayout()
        # title
        self.blood_temperature_title = QLabel('Blood Temperature [C\u00b0]')
        self.blood_temperature_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blood_temperature_title.setStyleSheet('background-color: #9d9ba2')
        # reading
        self.blood_temperature_value = QLabel('__')
        self.blood_temperature_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.blood_temperature_value.setStyleSheet('background-color: #c8dfff')
        # input line
        self.blood_temperature_input = QLineEdit()
        # adding to temp layout
        self.blood_temperature_vbox.addWidget(self.blood_temperature_title)
        self.blood_temperature_vbox.addWidget(self.blood_temperature_value)
        self.blood_temperature_vbox.addWidget(self.blood_temperature_input)
        # taking in temp input values once enter pressed
        self.blood_temperature_input.returnPressed.connect(lambda: self.write_txt(self.blood_temperature_input.text(), None, None))


        # flowrate stuff
        # layout
        self.flowrate_vbox = QVBoxLayout()
        # title
        self.flowrate_title = QLabel('Flowrate [L/min]')
        self.flowrate_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.flowrate_title.setStyleSheet('background-color: #9d9ba2')
        # reading
        self.flowrate_value = QLabel('__')
        self.flowrate_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.flowrate_value.setStyleSheet('background-color: #c8dfff')
        # input line
        self.flowrate_input = QLineEdit()
        # adding to flowrate layout
        self.flowrate_vbox.addWidget(self.flowrate_title)
        self.flowrate_vbox.addWidget(self.flowrate_value)
        self.flowrate_vbox.addWidget(self.flowrate_input)
        # taking in temp input values once enter pressed
        self.flowrate_input.returnPressed.connect(lambda: self.write_txt(None, self.flowrate_input.text(), None))


        # blood oxygen concentration stuff
        # layout
        self.oxygen_concentration_vbox = QVBoxLayout()
        # title
        self.oxygen_concentration_title = QLabel('Oxygen Concentration [%]')
        self.oxygen_concentration_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.oxygen_concentration_title.setStyleSheet('background-color: #9d9ba2')
        # reading
        self.oxygen_concentration_value = QLabel('__')
        self.oxygen_concentration_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.oxygen_concentration_value.setStyleSheet('background-color: #c8dfff')
        # input line
        self.oxygen_concentration_input = QLineEdit()
        # adding to temp layout
        self.oxygen_concentration_vbox.addWidget(self.oxygen_concentration_title)
        self.oxygen_concentration_vbox.addWidget(self.oxygen_concentration_value)
        self.oxygen_concentration_vbox.addWidget(self.oxygen_concentration_input)
        # taking in temp input values once enter pressed
        self.oxygen_concentration_input.returnPressed.connect(lambda: self.write_txt(None, None, self.oxygen_concentration_input.text()))


        # motor rpm stuff
        # layout
        self.motor_rpm_vbox = QVBoxLayout()
        # title
        self.motor_rpm_title = QLabel('Oxygen Concentration [%]')
        self.motor_rpm_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motor_rpm_title.setStyleSheet('background-color: #9d9ba2')
        # reading
        self.motor_rpm_value = QLabel('__')
        self.motor_rpm_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motor_rpm_value.setStyleSheet('background-color: #c8dfff')
        self.motor_rpm_input = QLineEdit()
        # adding to temp layout
        self.motor_rpm_vbox.addWidget(self.motor_rpm_title)
        self.motor_rpm_vbox.addWidget(self.motor_rpm_value)
        self.motor_rpm_vbox.addWidget(self.motor_rpm_input)


        # full layout
        self.hbox_layout.addLayout(self.blood_temperature_vbox,1)
        self.hbox_layout.addLayout(self.flowrate_vbox, 1)
        self.hbox_layout.addLayout(self.oxygen_concentration_vbox, 1)
        self.hbox_layout.addLayout(self.motor_rpm_vbox, 1)


    # function that runs the thread, called once when the pop up is closed
    def run_thread(self):
        # start the thread
        self.thread.start()


    # called by the thread with the list of new averages to be displayed
    def set_values(self, val_list):
        # printing the list of averages
        for value in val_list:
            print(value)

        # rests labels with new reading values
        self.blood_temperature_value.setText(str(val_list[0]))
        self.flowrate_value.setText(str(val_list[1]))
        self.oxygen_concentration_value.setText(str(val_list[2]))
        self.motor_rpm_value.setText(str(val_list[3])) 


    # writes to the serial monitor whenever enter is pressed in one of the input boxes
    def write_txt(self, temp, flowrate, oxygen):
        # resets whatever new value was just entered, with the values for the other variables staying the same
        
        # temp
        if temp is not None:
            self.temperature_input_value = 'ct' + str(temp)
            print(self.temperature_input_value)
            self.thread.print_to_monitor(self.temperature_input_value.encode('utf-8'))

        # flowrate
        if flowrate is not None:
            self.flowrate_input_value = 'cf' + str(flowrate)
            print(self.flowrate_input_value)
            self.thread.print_to_monitor(self.flowrate_input_value.encode('utf-8'))

        # oxygen
        if oxygen is not None:
            self.oxygen_input_value = 'co' + str(oxygen)
            print(self.oxygen_input_value)
            self.thread.print_to_monitor(self.oxygen_input_value.encode('utf-8'))



# run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    print('showing window')
    window.show()
    sys.exit(app.exec())