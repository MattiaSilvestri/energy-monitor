import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # type: ignore
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from random import randint
import datetime
from utils.data import compute_session_cumulative_consumption


# Plot Class
class PlotWindowApp(QWidget):
    """
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
    :param x_unit_measurement: letter corresponding to the unit of measurement for the x-axis (s: seconds, m: minutes, h:hours)
    :type x_unit_measurement: str
    :param y_unit_measurement: letter corresponding to the unit of measurement for the y-axis (s: seconds, m: minutes, h:hours)
    :type y_unit_measurement: str

    """

    def __init__(
        self,
        cpu_tdp,
        co2_intensity,
        time_interval,
        get_interval_emissions_method,
        appearance_params,
    ):
        super().__init__()

        # initialize attributes
        self.get_interval_emissions_method = get_interval_emissions_method
        self.time_interval = time_interval
        self.co2_intesity = co2_intensity
        self.cpu_tdp = cpu_tdp
        self.plot_position = appearance_params["Window"]["plot_position"]
        self.num_x_points = appearance_params["Plot"]["num_x_points"]
        self.num_x_ticks = appearance_params["Plot"]["num_x_ticks"]
        self.x_unit_measurement = appearance_params["Plot"]["x_unit_measurement"]
        self.y_unit_measurement = appearance_params["Plot"]["y_unit_measurement"]
        self.plot_font_size = appearance_params["Plot"]["font_size"]
        self.plot_font_weight = appearance_params["Plot"]["font_weight"]
        self.plot_grid_line_color = appearance_params["Plot"]["grid_line_color"]
        self.plot_grid_line_style = appearance_params["Plot"]["grid_line_style"]
        self.plot_grid_line_width = appearance_params["Plot"]["grid_line_width"]
        self.plot_line_color = appearance_params["Plot"]["line_color"]
        self.plot_line_alpha = appearance_params["Plot"]["line_alpha"]
        self.plot_area_color = appearance_params["Plot"]["area_color"]
        self.plot_area_alpha = appearance_params["Plot"]["area_alpha"]
        self.thread_running = False
        self.new_value = 0
        self.historical_y = 0

        # find y unit of measurement multiplier
        match self.y_unit_measurement:
            case "s":
                self.y_unit_multiplier = 1
            case "m":
                self.y_unit_multiplier = 60
            case "h":
                self.y_unit_multiplier = 3600
            case _:
                raise ValueError(
                    "Please enter a valid unit of measure for the y-axis. Choose between 's', 'm' or 'h'."
                )

        # initialize initial graphs values
        self.x = np.arange(self.num_x_points)[::-1] * -1
        self.y = self.x * 0

        # call initialization methods
        self.create_window()
        self.insert_ax()
        self.connect_timer()
        self.load_historical_data()

    def create_window(self):
        """
        This method creates a new window layout and prepare a white canvas where a plot can be drawn.
        """
        self.setWindowTitle("Energy Monitor Plot")
        layout = QVBoxLayout()
        self.setLayout(layout)
        fig = plt.Figure(figsize=(15, 3))
        self.canvas = FigureCanvas(fig)
        layout.addWidget(self.canvas)
        self.label = QLabel("Init Label", self)
        layout.addWidget(self.label)

    def insert_ax(self):
        """
        This method populate the empty canvas with a matplotlib axes structure.
        """
        # define matplotlib font properties
        font = {"weight": self.plot_font_weight, "size": self.plot_font_size}
        matplotlib.rc("font", **font)

        # create a matplotlib line plot structure
        self.ax = self.canvas.figure.subplots()
        self.ax.set_xlim([-self.num_x_points + 1, 0])
        self.set_labels_ticks(
            x_unit_measurement=self.x_unit_measurement, num_ticks=self.num_x_ticks
        )
        self.ax.set_ylabel(
            f"gCOeq \nevery {self.time_interval}{self.y_unit_measurement}",
            fontsize="small",
            horizontalalignment="right",
        )
        self.ax.set_xlabel(f"Time ({self.x_unit_measurement})")
        self.line_plot = None
        self.ax.set_position(self.plot_position)
        self.ax.grid(
            color=self.plot_grid_line_color,
            linestyle=self.plot_grid_line_style,
            linewidth=self.plot_grid_line_width,
        )
        self.session_label = self.ax.text(0, 0, "")
        self.historical_label = self.ax.text(0, 0, "")
        self.annotation = self.ax.annotate(
            "Session",
            (1.2, 0.99),
            xycoords="axes fraction",
            bbox=dict(boxstyle="round", fc="w"),
        )

    def connect_timer(self):
        """
        This method connect a periodic timer to functions for computing and displaying the co2 equivalent emissions.
        """
        self.timer = QTimer()
        self.timer.setInterval(1000 * self.time_interval)
        self.timer.timeout.connect(self.compute_new_value)
        self.timer.timeout.connect(self.update_chart)
        self.timer.start()

    def compute_new_value(self):
        """
        This method create a new thread for computing the co2 equivalent emissions, without occupy the GUI processes and therefore
         without freezing the application. The new thread is equipped with a worker containing the logics for retrieving the values of interest.
        The computed value is then signaled to the main thread and stored to be plotted soon.
        """
        if not self.thread_running:
            self.thread = QThread()
            self.worker = MyDataCollectorWorker(
                self.cpu_tdp,
                self.co2_intesity,
                self.time_interval,
                self.get_interval_emissions_method,
            )
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
        """
        This method changes the thread running status to False when the thread process is finished.
        """
        self.thread_running = False

    def closeEvent(self, event):
        print("Saving results and shutting down...")
        self.save_log()
        self.thread.quit()
        self.thread.wait()

    def update_new_value(self, value):
        """
        This method stores the new value to be plotted right after the worker computes it.

        :param value: equivalent co2 emission just computed by the worker
        :type value: float
        """
        self.new_value = value * self.y_unit_multiplier

    def update_chart(self):
        """
        This method update the data points to be plotted and display the new plot.
        """
        # update data to plot
        self.y = self.y[
            1:
        ]  # TODO: max session cache is the initial lenght of y, to save more plot data we need to split y_to_save and y_to_plot
        self.y = np.append(self.y, self.new_value)

        # update labels
        self.session_label.set_position((0.9, self.y.max() * 0.7))
        self.session_label.set_text(
            "SESSION\n"
            + str(
                round(
                    compute_session_cumulative_consumption(
                        self.y, self.x_unit_measurement, self.y_unit_measurement
                    ),
                    2,
                )
            )
            + " gCO2eq"
        )
        self.historical_label.set_position((0.9, self.y.max() * 0.3))
        self.historical_label.set_text(
            "HISTORICAL\n"
            + str(
                round(
                    compute_session_cumulative_consumption(
                        self.y, self.x_unit_measurement, self.y_unit_measurement
                    )
                    + self.historical_y,
                    2,
                )
            )
            + " gCO2eq"
        )

        # fill area under the line
        if self.ax.collections:
            self.ax.collections[0].remove()
        self.ax.fill_between(
            self.x, self.y, 0, color=self.plot_area_color, alpha=self.plot_area_alpha
        )

        # display updated plot
        if self.line_plot:
            self.line_plot[0].remove()
        self.line_plot = self.ax.plot(
            self.x, self.y, color=self.plot_line_color, alpha=self.plot_line_alpha
        )
        self.canvas.draw()

    def set_labels_ticks(self, num_ticks, x_unit_measurement):
        """
        This method find the correct labels to be set in the x-axis according to the prefered unit of measurement and number of ticks.

        :param num_ticks: number of ticks to be set in the x-axis
        :type num_ticks: int
        :param x_unit_measurement: letter corresponding to the unit of measurement for the x-axis (s: seconds, m: minutes, h:hours)
        :type x_unit_measurement: str
        """
        match x_unit_measurement:
            case "s":
                labels_all = self.x * self.time_interval
            case "m":
                labels_all = self.x * self.time_interval / 60
            case "h":
                labels_all = self.x * self.time_interval / 3600
            case _:
                raise ValueError(
                    "Please enter a valid unit of measure for the x-axis. Choose between 's', 'm' or 'h'."
                )
        ticks = np.linspace(self.x[0], self.x[-1], num_ticks)
        labels = labels_all[np.linspace(0, len(labels_all) - 1, num_ticks).astype(int)]
        labels_ticks = [str(round(element, 1)) for element in list(labels)]
        self.ax.set_xticks(ticks, labels_ticks)

    def load_historical_data(self):
        """
        This method loads all the txt data gathered during the previous sessions.
        """
        # get current file path
        current_file_path = Path(os.path.realpath(__file__))

        # get package root path
        data_path = (
            current_file_path.parent.absolute().parent.absolute().parent.absolute()
            / "data"
            / "userdata"
        )
        if data_path.exists():
            historical_data_files = list(data_path.iterdir())
            for file in historical_data_files:
                data = np.loadtxt(str(file))
                self.historical_y += compute_session_cumulative_consumption(
                    data, self.x_unit_measurement, self.y_unit_measurement
                )

    def save_log(self):
        """
        This method saves all the data gathered during the last session to a txt log file.
        """

        # remove leading zeros from data
        y_to_save = np.trim_zeros(self.y)

        # get current file path
        current_file_path = Path(os.path.realpath(__file__))

        # get package root path
        data_path = os.path.join(
            current_file_path.parent.absolute().parent.absolute().parent.absolute(),
            "data/userdata",
        )
        if not os.path.exists(data_path):
            os.makedirs(data_path)

        # get now string
        filename = "log_" + str(datetime.datetime.now()).split(".")[0].replace(
            ":", "-"
        ).replace(" ", "_")

        # save data to txt file
        np.savetxt(os.path.join(data_path, filename), y_to_save)


class MyDataCollectorWorker(QObject):
    """
    This class defines a supplementary worker that can compute the equivalent co2 emission without disturbing the GUI processes.

    :param cpu_tdp: CPU Thermal Design Power (TDP) in watts
    :type cpu_tdp: int
    :param co2_intensity: carbon intensity value for the selected country
    :type co2_intensity: float
    :param time_interval: frequency at which the plot updates and compute the CPU usage (in seconds)
    :type time_interval: int
    :param get_interval_emissions_method: method to compute the equivalent carbon emission
    :type get_interval_emissions_method: function

    """

    finished = pyqtSignal()
    progress = pyqtSignal(float)

    def __init__(
        self, cpu_tdp, co2_intensity, time_interval, get_interval_emissions_method
    ):
        super().__init__()
        self.get_interval_emissions_method = get_interval_emissions_method
        self.cpu_tdp = cpu_tdp
        self.co2_intesity = co2_intensity
        self.time_interval = time_interval

    def run(self):
        """
        This method call the function to compute the equivalent co2 emission and returns the value as a progress signal to the main thread.
        """
        value = self.get_interval_emissions_method(
            self.cpu_tdp, self.co2_intesity, self.time_interval
        )
        self.progress.emit(value)
        self.finished.emit()


# Test the GUI with random numbers generation
if __name__ == "__main__":
    from utils.io import safe_read_config

    # Read YAML file
    config = safe_read_config("config.yml")
    config_appearence = config["Appearance"]

    app = QApplication(sys.argv)
    app.setStyleSheet(
        """
        QWidget {
            font-size: 20px;
        }
    """
    )

    myApp = PlotWindowApp(
        cpu_tdp=15,
        co2_intensity=400,
        time_interval=1,
        get_interval_emissions_method=lambda x, y, z: randint(0, 10),
        appearance_params=config_appearence,
    )

    myApp.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Goodbye!")
