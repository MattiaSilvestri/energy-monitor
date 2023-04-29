import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from random import randint


class MyApp(QWidget):
    def __init__(self, cpu_tdp, co2_intensity, get_interval_emissions_method):
        super().__init__()
        self.setWindowTitle('Energy Monitor Plot')
        # self.window_width, self.window_height = 1200, 800
        # self.setMinimumSize(self.window_width, self.window_height)
        self.get_interval_emissions_method = get_interval_emissions_method

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.canvas = FigureCanvas(plt.Figure(figsize=(15, 3)))
        layout.addWidget(self.canvas)
        self.insert_ax()

        # some example data
        self.x = np.arange(200)[::-1]*-1
        self.y = self.x*0
        self.cpu_tdp = cpu_tdp
        self.co2_intesity = co2_intensity

        # timer
        self.timer = QTimer()
        self.timer.setInterval(1000)
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
        self.line_plot = None

    def update_chart(self):

        new_value =  self.get_interval_emissions_method(self.cpu_tdp, self.co2_intesity)  # randint(0,50)
        self.y = self.y[1:]  # Remove the first
        self.y = np.append(self.y, new_value)

        if self.line_plot:
            self.line_plot[0].remove()
        self.line_plot = self.ax.plot(self.x,self.y, color='g')
        self.canvas.draw()

if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 30px;
        }
    ''')
    
    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing Window...')