from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QSpinBox, QLineEdit
)
from PySide6.QtCore import Qt

from pathlib import Path

from util.hdf5_reader import HDF5Reader
from widgets.graph_widget import Graph
from timeKeeper import TimeKeeper


class TimelineWidget(QWidget):
    def __init__(self, time_keeper: TimeKeeper):
        super().__init__()

        self.time_keeper = time_keeper
        self.graph = Graph(None)

        self._create_layout()
        self._connect_timekeeper()

    def _parse_sensor_id(self, senor_id: str):
        return senor_id.split('_', 1)[1].rsplit('_', 1)[0]

    def load_data(self, data_path: str):
        old_graph = self.graph
        self.layout().removeWidget(old_graph)
        old_graph.deleteLater()

        reader = HDF5Reader(Path(data_path), idx_mode=False)
        self.graph = Graph(reader)

        if self.time_keeper is None:
            pos = 0
        else:
            pos = self.time_keeper.get_time()

        self.graph.update_position(pos)

        self.layout().addWidget(self.graph)

        self.label_a.setText(self._parse_sensor_id(self.graph.sensor_a))
        self.label_b.setText(self._parse_sensor_id(self.graph.sensor_b))

    def _create_layout(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(4)

        controls = self._build_controls()
        layout.addWidget(controls)
        layout.addWidget(self.graph, stretch=1)
        self.setLayout(layout)

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
        btn_a_plus.clicked.connect(lambda: self._on_btn(self.graph.sensor_a, "+"))
        btn_a_minus.clicked.connect(lambda: self._on_btn(self.graph.sensor_a, "-"))
        self.min_box_a.editingFinished.connect(
            lambda: self._on_min_edit(self.graph.sensor_a, self.min_box_a)
        )

        increment_label = QLabel("Increment")

        self.step_box = QSpinBox()
        self.step_box.setRange(1, 10000)
        self.step_box.setValue(50)
        self.step_box.setFixedHeight(20)
        self.step_box.setAlignment(Qt.AlignCenter)
        self.step_box.setButtonSymbols(QSpinBox.NoButtons)

        self.label_b = QLabel("BLUE")
        self.label_b.setAlignment(Qt.AlignCenter)
        self.label_b.setStyleSheet("color: #4488ff; font-weight: bold; font-size: 10px;")

        btn_b_plus = QPushButton("+")
        self.min_box_b = self._make_min_box()
        btn_b_minus = QPushButton("-")
        self._style_btn(btn_b_plus, "#4488ff")
        self._style_btn(btn_b_minus, "#4488ff")
        btn_b_plus.clicked.connect(lambda: self._on_btn(self.graph.sensor_b, "+"))
        btn_b_minus.clicked.connect(lambda: self._on_btn(self.graph.sensor_b, "-"))
        self.min_box_b.editingFinished.connect(
            lambda: self._on_min_edit(self.graph.sensor_b, self.min_box_b)
        )

        for w in (
                self.label_a,
                btn_a_plus,
                self.min_box_a,
                btn_a_minus,
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

    def _on_min_edit(self, sensor_id: str, box: QLineEdit):
        """min value was edited in the box"""
        try:
            new_min = int(box.text())
            self.graph.reader.set_min(sensor_id, new_min)
            self.graph.update_plot()
        except:
            self._refresh_min_box(sensor_id, box)

    def _refresh_min_box(self, sensor_id: str, box: QLineEdit):
        """Pull the current min from the backend and display it."""
        reader = self.graph.reader
        if reader is None:
            return
        current = reader.get_sensors()[sensor_id]
        box.blockSignals(True)
        box.setText(str(current))
        box.blockSignals(False)

    def _on_btn(self, sensor_id: str, direction: str):
        reader = self.graph.reader
        if reader is None:
            return
        amount = self.step_box.value()
        if direction == "-":
            amount *= -1
        self.graph.reader.adjust_min(sensor_id, amount)
        self.graph.update_plot()

        box = self.min_box_a if sensor_id == self.graph.sensor_a else self.min_box_b
        self._refresh_min_box(sensor_id, box)

    def _connect_timekeeper(self):
        self.time_keeper.positionChanged.connect(self._on_position_changed)

    def _on_position_changed(self, position):
        position += self.time_keeper.get_trim()
        self.graph.update_position(position)
