from PySide6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

from util.hdf5_reader import HDF5Reader


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        hr = [v / 1000 // 3600 for v in values]
        min = [v / 1000 // 60 % 60 for v in values]
        sec = [v // 1000 % 60 for v in values]
        mil = [v % 1000 for v in values]

        strings = []
        for i in range(len(values)):
            if values[i] < 0:
                strings.append("")
            else:
                strings.append("%.2d:%.2d:%.2d:%.3d" % (hr[i], min[i], sec[i], mil[i]))
        return strings

class Graph(QWidget):
    def __init__(self, reader: HDF5Reader):
        super().__init__()

        self.reader = reader

        self.current_time = 0
        self.margin = 10000 # ms

        # single plot
        self._plot_init()
        self._create_ui()

        # leave empty plot if no data
        if self.reader is None:
            return

        self._sensor_init()
        self._curve_init()
        self._find_offset()

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
            x_a = data_a[:, 1] - self.offset_a
            self.curve_a.setData(x_a, y_a)

        # --- SENSOR B ---
        if data_b is not None and len(data_b) > 0:
            y_b = data_b[:, 0]
            x_b = data_b[:, 1] - self.offset_b
            self.curve_b.setData(x_b, y_b)

        self.plot.setXRange(self.current_time - self.margin, self.current_time + self.margin, 0)
        self.vline.setPos(self.current_time)

    def update_position(self, position):
        self.current_time = position
        self.update_plot()

    def _plot_init(self):
        axis = TimeAxisItem(orientation="bottom")
        self.plot = pg.PlotWidget(axisItems={"bottom": axis})
        self.plot.setMouseEnabled(x=False, y=False)

        if self.reader is None:
            return

        # multiply by 1.05 in order to only pad the top
        self.plot.setYRange(0, self.reader.accl_range * 1.05, 0)
        self.vline = pg.InfiniteLine(pen=pg.mkPen("w", width=2))
        self.plot.addItem(self.vline)

    def _sensor_init(self):
        # get sensors (assumes 2)
        sensors = list(self.reader.get_sensors().keys())
        if len(sensors) < 2:
            raise ValueError("Need at least 2 sensors to overlay")

        self.sensor_a = sensors[0]
        self.sensor_b = sensors[1]

    def _curve_init(self):
        # two curves (different colors)
        self.curve_a = self.plot.plot(pen="r", name=self.sensor_a)
        self.curve_b = self.plot.plot(pen="b", name=self.sensor_b)

        # optional legend
        self.plot.addLegend()

    def _find_offset(self):
        # chunks.get() = [data, start, stop]
        # data = [[val,time]]
        # data[0][1] = first time

        # temporary toggle to get only first item
        self.reader.idx_mode = True
        chunks = self.reader.get_chunks_by_time(0, 1)
        self.reader.idx_mode = False

        self.offset_a = chunks.get(self.sensor_a)[0][0][1]
        self.offset_b = chunks.get(self.sensor_b)[0][0][1]