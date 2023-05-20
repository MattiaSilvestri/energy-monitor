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
    '''
    This class defines a new window containing a dynamic line plot.
    
    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :param time_interval: frequency at which the plot updates and compute the CPU usage (in seconds)
    :type time_interval: int
    :param get_interval_emissions_method: method to compute the equivalent carbon emission
    :type get_interval_emissions_method: function
    :param num_x_points: number of points to be plotted in the x-axis
    :type num_x_points: int
    :param num_x_ticks: number of ticks to be set in the x-axis
    :type num_x_ticks: int
    :param unit_measurement: letter corresponding to the unit of measurement for the x-axis (s: seconds, m: minutes, h:hours)
    :type unit_measurement: str
    
    '''
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
        '''
        This method creates a new window layout and prepare a white canvas where a plot can be drawn.
        '''
        self.setWindowTitle('Energy Monitor Plot')
        layout = QVBoxLayout()
        self.setLayout(layout)
        fig = plt.Figure(figsize=(15, 3))
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)

    def insert_ax(self):
        '''
        This method populate the empty canvas with a matplotlib axes structure.
        '''
        # define matplotlib font properties
        font = {
            'weight': 'normal',
            'size': 10
        }
        matplotlib.rc('font', **font)

        # create a matplotlib line plot structure
        self.ax = self.canvas.figure.subplots()
        self.ax.set_xlim([-self.num_x_points, 0])
        self.set_labels_ticks(unit_measurement=self.unit_measurement, num_ticks=self.num_x_ticks)
        self.ax.set_ylabel(f"gCOeq \nevery {self.time_interval}s", fontsize="small", rotation="horizontal", horizontalalignment="right")
        self.ax.set_xlabel("Time")
        self.line_plot = None
        self.ax.set_position([0.1, 0.2, 0.85, 0.7]) #left,bottom,width,height 

    def connect_timer(self):
        '''
        This method connect a periodic timer to functions for computing and displaying the co2 equivalent emissions.
        '''
        self.timer = QTimer()
        self.timer.setInterval(1000*self.time_interval)
        self.timer.timeout.connect(self.compute_new_value)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start()

    def compute_new_value(self):
        '''
        This method create a new thread for computing the co2 equivalent emissions, without occupy the GUI processes and therefore
         without freezing the application. The new thread is equipped with a worker containing the logics for retrieving the values of interest.
        The computed value is then signaled to the main thread and stored to be plotted soon.
        '''
        if not self.thread_running:
            self.thread = QThread()
            self.worker = MyDataCollectorWorker(self.cpu_tdp, self.co2_intesity, self.time_interval, self.get_interval_emissions_method)
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.signal_thread_finish)
            self.worker.progress.connect(self.update_new_value)
            self.thread_running = True
            self.thread.start()

    def signal_thread_finish(self):
        '''
        This method changes the thread running status to False when the thread process is finished.
        '''
        self.thread_running = False
    
    def update_new_value(self, value):
        '''
        This method stores the new value to be plotted right after the worker computes it.
        
        :param value: equivalent co2 emission just computed by the worker
        :type value: float
        '''
        self.new_value = value

    def update_chart(self):
        '''
        This method update the data points to be plotted and display the new plot.
        '''  
        # update data to plot
        self.y = self.y[1:]
        self.y = np.append(self.y, self.new_value)

        # display updated plot
        if self.line_plot:
            self.line_plot[0].remove()
        self.line_plot = self.ax.plot(self.x,self.y, color='g')
        self.canvas.draw()

    def set_labels_ticks(self, num_ticks, unit_measurement):
        '''
        This method find the correct labels to be set in the x-axis according to the prefered unit of measurement and number of ticks.

        :param num_ticks: number of ticks to be set in the x-axis
        :type num_ticks: int
        :param unit_measurement: letter corresponding to the unit of measurement for the x-axis (s: seconds, m: minutes, h:hours)
        :type unit_measurement: str
        '''  
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


class MyDataCollectorWorker(QObject):
    '''
    This class defines a supplementary worker that can compute the equivalent co2 emission without disturbing the GUI processes.
    
    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :param time_interval: frequency at which the plot updates and compute the CPU usage (in seconds)
    :type time_interval: int
    :param get_interval_emissions_method: method to compute the equivalent carbon emission
    :type get_interval_emissions_method: function
    
    '''
    finished = pyqtSignal()
    progress = pyqtSignal(float)

    def __init__(self, cpu_tdp, co2_intensity, time_interval, get_interval_emissions_method):
        super().__init__()
        self.get_interval_emissions_method = get_interval_emissions_method
        self.cpu_tdp = cpu_tdp
        self.co2_intesity = co2_intensity
        self.time_interval = time_interval

    def run(self):
        '''
        This method call the function to compute the equivalent co2 emission and returns the value as a progress signal to the main thread.
        '''
        value = self.get_interval_emissions_method(self.cpu_tdp, self.co2_intesity, self.time_interval)
        self.progress.emit(value)
        self.finished.emit()


# Test the GUI with random numbers generation
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