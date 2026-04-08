import pyqtgraph as pg
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt
from util.hdf5_reader import HDF5Reader
from pathlib import Path
from timeKeeper import TimeKeeper

class TimelineWidget(QWidget):
    def __init__(self, timekeeper: TimeKeeper):
        super().__init__()
        self.time_keeper = timekeeper
        self.data_reader = None
        self.graph = pg.PlotWidget()
        self._create_ui()

        self.time_keeper.positionChanged.connect(self._on_position_changed)
        self.time_keeper.windowChanged.connect(self._on_window_changed)

    def _create_ui(self):
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(4, 4, 4, 4)
        outer_layout.setSpacing(6)

        controls = self._build_controls()
        outer_layout.addWidget(controls)
        outer_layout.addWidget(self.graph, stretch=1)

        self.setLayout(outer_layout)

    def _build_controls(self) -> QWidget:
        panel = QWidget()
        panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        panel.setFixedWidth(52)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignTop)

        self.label_a = QLabel("RED")
        self.label_a.setAlignment(Qt.AlignCenter)
        self.label_a.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 10px;")

        btn_a_plus = QPushButton("+")
        self.min_box_a = self._make_min_box()
        btn_a_minus = QPushButton("-")
        self._style_btn(btn_a_plus, "#ff4444")
        self._style_btn(btn_a_minus, "#ff4444")
        btn_a_plus.clicked.connect(lambda: self._on_btn(self.sensor_a, "+"))
        btn_a_minus.clicked.connect(lambda: self._on_btn(self.sensor_a, "-"))
        self.min_box_a.editingFinished.connect(
            lambda: self._on_min_edit(self.sensor_a, self.min_box_a)
        )

        increment_label = QLabel("Increment")

        self.step_box = QSpinBox()
        self.step_box.setRange(1, 10000)
        self.step_box.setValue(50)
        self.step_box.setFixedHeight(20)
        self.step_box.setAlignment(Qt.AlignCenter)
        self.step_box.setButtonSymbols(QSpinBox.NoButtons)

        get_mins_box = QPushButton("Get Mins")
        get_mins_box.clicked.connect(self._get_mins)

        self.label_b = QLabel("BLUE")
        self.label_b.setAlignment(Qt.AlignCenter)
        self.label_b.setStyleSheet("color: #4488ff; font-weight: bold; font-size: 10px;")

        btn_b_plus = QPushButton("+")
        self.min_box_b = self._make_min_box()
        btn_b_minus = QPushButton("-")
        self._style_btn(btn_b_plus, "#4488ff")
        self._style_btn(btn_b_minus, "#4488ff")
        btn_b_plus.clicked.connect(lambda: self._on_btn(self.sensor_b, "+"))
        btn_b_minus.clicked.connect(lambda: self._on_btn(self.sensor_b, "-"))
        self.min_box_b.editingFinished.connect(
            lambda: self._on_min_edit(self.sensor_b, self.min_box_b)
        )

        for w in (
                self.label_a, 
                btn_a_plus,
                self.min_box_a,
                btn_a_minus, 
                get_mins_box,
                increment_label,
                self.step_box,
                self.label_b, 
                btn_b_plus, 
                self.min_box_b,
                btn_b_minus
            ):
            layout.addWidget(w)

        layout.addStretch()
        return panel

    @staticmethod
    def _style_btn(btn: QPushButton, color: str):
        btn.setFixedSize(40, 15)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}33;
            }}
            QPushButton:pressed {{
                background-color: {color}66;
            }}
        """)

    @staticmethod
    def _make_min_box() -> QLineEdit:
        box = QLineEdit("0")
        box.setFixedHeight(20)
        box.setAlignment(Qt.AlignCenter)
        box.setStyleSheet("font-size: 10px;")
        return box

    def load_data(self, datapath: str):
        del self.data_reader
        self.graph.clear()
        self.data_reader = HDF5Reader(Path(datapath))
        sensors = list(self.data_reader.get_sensors().keys())
        if len(sensors) < 2:
            raise ValueError("Need at least 2 sensors to overlay")
        self.sensor_a = sensors[0]
        self.sensor_b = sensors[1]
        self.label_a.setText(self._parse_sensor_id(self.sensor_a))
        self.label_b.setText(self._parse_sensor_id(self.sensor_b))
        self.curve_a = self.graph.plot(pen=pg.mkPen("r", width=2), name=self.sensor_a)
        self.curve_b = self.graph.plot(pen=pg.mkPen("b", width=2), name=self.sensor_b)
        self.vline = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen("w", width=2))
        self.graph.addItem(self.vline)

        self._refresh_min_box(self.sensor_a, self.min_box_a)
        self._refresh_min_box(self.sensor_b, self.min_box_b)

    def _on_min_edit(self, sensor_id: str, box: QLineEdit):
        """min value was edited in the box"""
        try:
            new_min = int(box.text())
        except:
            self._refresh_min_box(sensor_id, box)
            return
        self.data_reader.set_min(sensor_id, new_min)
        self._on_position_changed(self.time_keeper.get_time())

    def _refresh_min_box(self, sensor_id: str, box: QLineEdit):
        """Pull the current min from the backend and display it."""
        if self.data_reader is None:
            return
        current = self.data_reader.get_sensors()[sensor_id]
        box.blockSignals(True)
        box.setText(str(current))
        box.blockSignals(False)

    def _get_mins(self):
        print(self.data_reader.get_sensors())

    def _parse_sensor_id(self, senor_id: str):
        return senor_id.split('_', 1)[1].rsplit('_', 1)[0]

    def _on_btn(self, sensor_id: str, direction: str):
        if self.data_reader is None:
            return
        amount = self.step_box.value()
        if direction == "-":
            amount *= -1
        self.data_reader.adjust_min(sensor_id, amount)
        self._on_position_changed(self.time_keeper.get_time())

        box = self.min_box_a if sensor_id == self.sensor_a else self.min_box_b
        self._refresh_min_box(sensor_id, box)

    def _on_position_changed(self, position):
        if self.data_reader is None:
            return
        
        chunks = self.data_reader.get_chunks_by_time(position, margin_ms=10000)
        data_a, start_a, stop_a = chunks.get(self.sensor_a)
        data_b, start_b, stop_b = chunks.get(self.sensor_b)

        if hasattr(self, "vline"):
            self.vline.setPos(position / 1000)

        if data_a is not None and len(data_a) > 0:
            y_a = data_a[:, 0]
            sync_ts_a = self.data_reader.get_sync_timestamp(self.sensor_a)
            x_a = (data_a[:, 1] - sync_ts_a) / 1000            
            self.curve_a.setData(x_a, y_a)

        if data_b is not None and len(data_b) > 0:
            y_b = data_b[:, 0]
            sync_ts_b = self.data_reader.get_sync_timestamp(self.sensor_b)
            x_b = (data_b[:, 1] - sync_ts_b) / 1000
            self.curve_b.setData(x_b, y_b)

    def _on_window_changed(self, start, end):
        print(start, end)