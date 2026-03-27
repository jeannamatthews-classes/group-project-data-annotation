import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import numpy as np

from pathlib import Path
from util.hdf5_reader import HDF5Reader

class WaveformViewer(QMainWindow):
    def __init__(self, reader):
        super().__init__()
        self.reader = reader

        self.setWindowTitle("Overlay Waveform Viewer")

        # single plot
        self.plot = pg.PlotWidget()
        self.setCentralWidget(self.plot)

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
        self.margin = 5000  # ms

        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

        self.reader.set_min(self.sensor_b, 300)

    def update_plot(self):
        chunks = self.reader.get_chunks(self.current_time, self.margin)

        data_a, start_a, stop_a = chunks.get(self.sensor_a)
        data_b, start_b, stop_b = chunks.get(self.sensor_b)
        # --- SENSOR A ---
        if data_a is not None and len(data_a) > 0:
            y_a = data_a[:, 0]

            # reconstruct index axis
            # x_a = np.arange(start_a, stop_a) / self.reader.sample_rate
            x_a = np.arange(len(y_a))

            self.curve_a.setData(x_a, y_a)

        # --- SENSOR B ---
        if data_b is not None and len(data_b) > 0:
            y_b = data_b[:, 0]

            # x_b = np.arange(start_b, stop_b) / self.reader.sample_rate
            x_b = np.arange(len(y_b))
            self.curve_b.setData(x_b, y_b) 

        # print(len(y_a), len(y_b))

        self.current_time += 50

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_path = "C:\\Computer Science Programs\\hd_medical\\AgiMon\\align_data\\data\\hdf5_files\\session_2026-03-12_16_50_28.h5"
    reader = HDF5Reader(Path(file_path), idx_mode=False)

    viewer = WaveformViewer(reader)
    viewer.resize(1000, 800)
    viewer.show()

    sys.exit(app.exec())