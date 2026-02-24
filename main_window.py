from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from widgets.videoWidget import VideoWidget
from widgets.timelineWidget import TimelineWidget
from widgets.commentsWidget import CommentWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor Layout")
        self.resize(1200, 800)

        self._create_widgets()
        self._create_layout()
        self._create_menu()

    def _create_widgets(self):
        self.video_pane = VideoWidget()
        self.timeline = TimelineWidget()
        self.comments = CommentWidget()

    def _create_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # MAIN horizontal layout
        main_layout = QHBoxLayout(central_widget)

        # LEFT vertical layout (Video + Timeline)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.video_pane, stretch=3)
        left_layout.addWidget(self.timeline, stretch=1)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, stretch=4)
        main_layout.addWidget(self.comments, stretch=1)

    # Menu Bar
    def _create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)