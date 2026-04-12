from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy, QSpinBox, QLineEdit
)

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
        self._connect_signals()

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

    def _create_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.graph)
        self.setLayout(layout)

    def _connect_signals(self):
        self.time_keeper.positionChanged.connect(self._on_position_changed)
        self.time_keeper.windowChanged.connect(self._on_window_changed)

    def _on_position_changed(self, position):
        self.graph.update_position(position)

    def _on_window_changed(self, start, end):
        pass
