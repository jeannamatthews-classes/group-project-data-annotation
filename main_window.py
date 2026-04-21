from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFileDialog,
)

from timeKeeper import TimeKeeper
from widgets.videoWidget import VideoWidget
from widgets.timelineWidget import TimelineWidget
from widgets.commentsWidget import CommentWidget
from util.span_keeper import SpanKeeper

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor Layout")
        self.resize(1200, 800)

        self.time_keeper = TimeKeeper()

        self._create_widgets()
        self._create_layout()
        self._create_menu()

    def _create_widgets(self):
        self.video_pane = VideoWidget(SpanKeeper(), self.time_keeper)

        self.timeline = TimelineWidget(self.time_keeper)
        self.comments = CommentWidget(self.time_keeper)

        self.comments.commentsChanged.connect(self._sync_comments)
        self.comments.jumpRequested.connect(self.video_pane.player.setPosition)
        self.video_pane.commentClicked.connect(self._on_video_comment_clicked)

    def _sync_comments(self):
        comments = self.comments.get_comments()
        self.video_pane.set_comments(comments)

    def _on_video_comment_clicked(self, index: int, timestamp_ms: int):
        self.comments.select_comment_by_index(index)

    def _create_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # MAIN horizontal layout
        main_layout = QHBoxLayout(central_widget)

        # LEFT vertical layout (Video + Timeline)
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.video_pane, stretch=2)
        left_layout.addWidget(self.timeline, stretch=1)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, stretch=4)
        main_layout.addWidget(self.comments, stretch=1)

    def _load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv);;All Files (*)"
        )

        if file_path:
            self.video_pane.load_video(file_path)
            self.video_pane.play()

    def _load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Sensor Data File",
            "",
            "HDF5 Files (*.hdf *.h5 *.hdf5 *.he5);;All Files (*)"
        )

        if file_path:
            self.timeline.load_data(file_path)

    # Menu Bar
    def _create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        load_video_action = file_menu.addAction("Load Video")
        load_video_action.triggered.connect(self._load_video)

        load_data_action = file_menu.addAction("Load Data")
        load_data_action.triggered.connect(self._load_data)

        load_json_action = file_menu.addAction("Load JSON")
        load_json_action.triggered.connect(self.comments.comment_keeper.import_json_comments)

        save_json_action = file_menu.addAction("Save JSON")
        save_json_action.triggered.connect(self.comments.comment_keeper.save_json_comments)

        save_json_action = file_menu.addAction("Save JSON As")
        save_json_action.triggered.connect(
            lambda: self.comments.comment_keeper.save_json_comments(True)
        )

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)