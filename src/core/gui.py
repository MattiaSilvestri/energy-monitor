import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from random import randint

# Plot Class
class PlotWindowApp(QWidget):
    def __init__(self, cpu_tdp, co2_intensity, time_interval, get_interval_emissions_method, num_x_points, num_x_ticks, unit_measurement):
        super().__init__()

        # initialize attributes
        self.get_interval_emissions_method = get_interval_emissions_method
        self.time_interval = time_interval
        self.co2_intesity = co2_intensity
        self.cpu_tdp = cpu_tdp
        self.num_x_points = num_x_points
        self.num_x_ticks = num_x_ticks
        self.unit_measurement = unit_measurement
        self.thread_running = False
        self.new_value = 0

        # initialize initial graphs values
        self.x = np.arange(num_x_points)[::-1]*-1
        self.y = self.x*0

        # call initialization methods
        self.create_window()
        self.insert_ax()
        self.connect_timer()

    def create_window(self):
        self.setWindowTitle('Energy Monitor Plot')
        # self.setMinimumSize(self.window_width, self.window_height)
        layout = QVBoxLayout()
        self.setLayout(layout)
        fig = plt.Figure(figsize=(15, 3))
        fig.tight_layout()
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)

    def insert_ax(self):
        font = {
            'weight': 'normal',
            'size': 10
        }
        matplotlib.rc('font', **font)

        # create a matplotlib line plot
        self.ax = self.canvas.figure.subplots()
        self.ax.set_xlim([-self.num_x_points, 0])
        self.set_labels_ticks(unit_measurement=self.unit_measurement, num_ticks=self.num_x_ticks)
        self.ax.set_ylabel(f"gCOeq \nevery {self.time_interval}s", fontsize="small", rotation="horizontal", horizontalalignment="right")
        self.ax.set_xlabel("Time")
        self.line_plot = None
        self.ax.set_position([0.1, 0.2, 0.85, 0.75]) #left,bottom,width,height 

    def connect_timer(self):
        # connect timer to cyclic functions
        self.timer = QTimer()
        self.timer.setInterval(1000*self.time_interval)
        self.timer.timeout.connect(self.compute_new_value)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start()

    def set_labels_ticks(self, unit_measurement, num_ticks):
        if unit_measurement == "s":
            labels_all = self.x * self.time_interval
        elif unit_measurement == "m":
            labels_all = self.x * self.time_interval / 60
        elif unit_measurement == "h":
            labels_all = self.x * self.time_interval / 3600
        else:
            raise ValueError("Please enter a valid unit of measure. Choose between 's', 'm' or 'h'.")
        ticks = np.linspace(self.x[0],self.x[-1], num_ticks)
        labels = labels_all[np.linspace(0,len(labels_all)-1, num_ticks).astype(int)]
        labels_ticks = [str(round(element, 1))+unit_measurement for element in list(labels)]
        self.ax.set_xticks(ticks, labels_ticks)


    def compute_new_value(self):
        if not self.thread_running:
            self.thread = QThread()
            self.worker = MyDataCollectorWorker(self.cpu_tdp, self.co2_intesity, self.time_interval, self.get_interval_emissions_method)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.set_thread_running_status)
            self.worker.progress.connect(self.update_new_value)
            self.thread_running = True
            self.thread.start()
    
    def update_new_value(self, value):
        self.new_value = value

    def set_thread_running_status(self):
        self.thread_running = False

    def update_chart(self):
        # update data to plot
        self.y = self.y[1:]
        self.y = np.append(self.y, self.new_value)

        # update plot
        if self.line_plot:
            self.line_plot[0].remove()
        self.line_plot = self.ax.plot(self.x,self.y, color='g')
        self.canvas.draw()


class MyDataCollectorWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(float)

    def __init__(self, cpu_tdp, co2_intensity, time_interval, get_interval_emissions_method):
        super().__init__()
        self.get_interval_emissions_method = get_interval_emissions_method
        self.cpu_tdp = cpu_tdp
        self.co2_intesity = co2_intensity
        self.time_interval = time_interval

    def run(self):
        """Long-running task."""
        value = self.get_interval_emissions_method(self.cpu_tdp, self.co2_intesity, self.time_interval)
        self.progress.emit(value)
        self.finished.emit()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 20px;
        }
    ''')

    myApp = PlotWindowApp(cpu_tdp=15, co2_intensity=400, time_interval=1, get_interval_emissions_method=lambda x,y,z : randint(0,10), num_x_points=200, num_x_ticks=5, unit_measurement="m")
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')