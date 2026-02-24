from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class VideoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.label = QLabel("Video Section")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black; color: white;")

        layout.addWidget(self.label)