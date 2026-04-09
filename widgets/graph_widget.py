from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np
from datetime import datetime

from util.hdf5_reader import HDF5Reader


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        size = len(values)
        hr = [0] * size
        min = [0] * size
        sec = [0] * size
        mil = [0] * size

        for i, v in enumerate(values):
            hr[i] = v / 1000 // 3600
            min[i] = v / 1000 // 60 % 60
            sec[i] = v // 1000 % 60
            mil[i] = v % 1000

        return ["%.2d:%.2d%.2d:%.4d" % (hr[i], min[i], sec[i], mil[i]) for i in range(len(values))]

class Graph(QWidget):
    def __init__(self, reader: HDF5Reader):
        super().__init__()

        self.reader = reader

        # single plot
        self._plot_init()
        self._create_ui()

        if not self.reader:
            return

        # get sensors (assumes 2)
        sensors = list(self.reader.get_sensors().keys())
        if len(sensors) < 2:
            raise ValueError("Need at least 2 sensors to overlay")

        self.sensor_a = sensors[0]
        self.sensor_b = sensors[1]

        # two curves (different colors)
        self.curve_a = self.plot.plot(pen="r", name=self.sensor_a)
        self.curve_b = self.plot.plot(pen="b", name=self.sensor_b)

        # optional legend
        self.plot.addLegend()

        # time state
        self.current_time = 0
        self.margin = 500 # ms

        self.reader.set_min(self.sensor_b, 300)

    def _plot_init(self):
        axis = TimeAxisItem(orientation='bottom')
        self.plot = pg.PlotWidget(axisItems={'bottom': axis})
        self.plot.setMouseEnabled(x=False, y=False)

        if self.reader is None:
            return
        self.plot.setYRange(-self.reader.accl_range, self.reader.accl_range)

    def _create_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.plot)
        self.setLayout(layout)

    def update_plot(self):
        chunks = self.reader.get_chunks_by_time(self.current_time, self.margin)

        data_a, *_ = chunks.get(self.sensor_a)
        data_b, *_ = chunks.get(self.sensor_b)
        # --- SENSOR A ---
        if data_a is not None and len(data_a) > 0:
            y_a = data_a[:, 0]

            # reconstruct index axis
            x_a = np.arange(len(y_a))
            self.curve_a.setData(x_a, y_a)

        # --- SENSOR B ---
        if data_b is not None and len(data_b) > 0:
            y_b = data_b[:, 0]

            x_b = np.arange(len(y_b))
            self.curve_b.setData(x_b, y_b)

    def update_position(self, position):
        self.current_time = position
        self.update_plot()