import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from random import randint


class MyApp(QWidget):
    def __init__(self, cpu_tdp, co2_intensity, time_interval, get_interval_emissions_method):
        super().__init__()
        self.setWindowTitle('Energy Monitor Plot')
        # self.window_width, self.window_height = 1200, 800
        # self.setMinimumSize(self.window_width, self.window_height)
        self.get_interval_emissions_method = get_interval_emissions_method
        self.time_interval = time_interval
        self.new_value = 0
        self.thread_running = False

        # some example data
        self.x = np.arange(200)[::-1]*-1
        self.y = self.x*0
        self.cpu_tdp = cpu_tdp
        self.co2_intesity = co2_intensity

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(plt.Figure(figsize=(15, 3)))
        layout.addWidget(self.canvas)
        self.insert_ax()

        # timer
        self.timer = QTimer()
        self.timer.setInterval(1000*self.time_interval)
        self.timer.timeout.connect(self.compute_new_value)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start()

    def insert_ax(self):
        font = {
            'weight': 'normal',
            'size': 16
        }
        matplotlib.rc('font', **font)
        self.ax = self.canvas.figure.subplots()
        self.ax.set_xlim([-200, 0])

        labels_all = self.x * self.time_interval / 60
        labels = labels_all[np.linspace(0,len(labels_all)-1, 9).astype(int)]
        labels_ticks = [str(round(element, 1))+"min" for element in list(labels)]
        self.ax.set_xticklabels(labels_ticks)

        self.ax.set_ylabel(f"gCOeq \nevery {self.time_interval}s", fontsize="small", rotation="horizontal", horizontalalignment="right")
        self.ax.set_xlabel("Time")
        self.line_plot = None

    # def compute_new_value(self):
    #     self.new_value = self.get_interval_emissions_method(self.cpu_tdp, self.co2_intesity, self.time_interval)
    #     #self.new_value = randint(0,50)

    def compute_new_value(self):
        if not self.thread_running:
            # Step 2: Create a QThread object
            self.thread = QThread()
            # Step 3: Create a worker object
            self.worker = MyDataCollectorWorker(self.cpu_tdp, self.co2_intesity, self.time_interval, self.get_interval_emissions_method)
            # Step 4: Move worker to the thread
            self.worker.moveToThread(self.thread)
            # Step 5: Connect signals and slots
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.finished.connect(self.set_thread_running_status)
            self.worker.progress.connect(self.update_new_value)
            # Step 6: Start the thread
            self.thread_running = True
            self.thread.start()
    
    def update_new_value(self, value):
        self.new_value = value

    def set_thread_running_status(self):
        self.thread_running = False


    def update_chart(self):
        self.y = self.y[1:]
        self.y = np.append(self.y, self.new_value)

        if self.line_plot:
            self.line_plot[0].remove()
        self.line_plot = self.ax.plot(self.x,self.y, color='g')
        # self.ax.set_ylim([0, self.y[-20:].max()])
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
        #value = randint(0,50)
        self.progress.emit(value)
        self.finished.emit()




if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 30px;
        }
    ''')
    
    myApp = MyApp(15, 400, 1, lambda x,y,z : randint(0,10))
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')