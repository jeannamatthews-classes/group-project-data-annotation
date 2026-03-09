from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class CommentWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel("Comments Section")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #222; color: white;")

        layout.addWidget(self.label)

    def connect_signals(self, time_keeper):
        time_keeper.positionChanged.connect(self._on_position_changed)

    def _on_position_changed(self, position):
        pass