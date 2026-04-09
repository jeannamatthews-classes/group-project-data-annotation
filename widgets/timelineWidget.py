from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QSpinBox, QLineEdit
)

from pathlib import Path

from util.hdf5_reader import HDF5Reader
from widgets.graph_widget import Graph
from timeKeeper import TimeKeeper


class TimelineWidget(QWidget):
    def __init__(self, data_path: str | None = None):
        super().__init__()

        self.graph = Graph(data_path)

        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.graph)
        self.setLayout(layout)

    def load_data(self, data_path: str):
        old_graph = self.graph
        self.layout().removeWidget(old_graph)
        old_graph.deleteLater()

        reader = HDF5Reader(Path(data_path), idx_mode=False)
        self.graph = Graph(reader)
        self.layout().addWidget(self.graph)
        self.graph.update_position(0)

    def connect_signals(self, time_keeper: TimeKeeper):
        time_keeper.positionChanged.connect(self._on_position_changed)
        time_keeper.windowChanged.connect(self._on_window_changed)

    def _on_position_changed(self, position):
        self.graph.update_position(position)

    def _on_window_changed(self, start, end):
        pass
