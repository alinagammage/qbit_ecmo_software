import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.figure import Figure
from matplotlib.backends import backend_qt5agg 
from PyQt6.QtCore import QTimer

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create a Figure object and add a subplot
        self.figure = Figure()
        self.canvas = backend_qt5agg.FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_plot(self):
        # Clear the previous plot
        self.axes.clear()

        # Add your live plotting logic here
        # For example:
        x_data = [1,2,3,4]
        y_data = [1,2,3,4]
        self.axes.plot(x_data, y_data)

        # Update the plot
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Live Matplotlib Graph")
        self.widget = MatplotlibWidget()
        self.setCentralWidget(self.widget)

        # Create a QTimer for updating the plot at regular intervals
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Update every second
        self.timer.timeout.connect(self.widget.update_plot)
        self.timer.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
