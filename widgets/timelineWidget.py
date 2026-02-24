from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class TimelineWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel("Timeline Section")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #333; color: white;")

        layout.addWidget(self.label)