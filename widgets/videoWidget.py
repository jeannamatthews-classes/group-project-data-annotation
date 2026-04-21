from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QLabel, QCheckBox, QLineEdit
from PySide6.QtMultimedia import QMediaPlayer, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer, Qt, Signal
from PySide6.QtGui import QIntValidator
from widgets.highlight_slider import HighlightSlider
from timeKeeper import TimeKeeper
from util.span_keeper import SpanKeeper
from widgets.comment_marker_strip import CommentMarkerStrip

class VideoWidget(QWidget):
    commentClicked = Signal(int, int)
    def __init__(self, span_keeper: SpanKeeper, time_keeper: TimeKeeper | None = None):
        super().__init__()
        self.time_keeper = time_keeper
        self.span_keeper = span_keeper
        self.start_mark_set = False
        self.trim_start_ms = 0
        self.fps = None
        self.total_duration = None
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget, stretch=1)
        self.player = QMediaPlayer()
        self.time_keeper.set_player(self.player)
        self.player.setVideoOutput(self.video_widget)

        self.comment_strip = CommentMarkerStrip()
        layout.addWidget(self.comment_strip)

        scrubber_layout = QHBoxLayout()
        self.scrubber = HighlightSlider(Qt.Orientation.Horizontal, self.span_keeper)
        self.scrubber.setRange(0, 0)
        scrubber_layout.addWidget(self.scrubber)
        layout.addLayout(scrubber_layout)

        time_label_layout = QHBoxLayout()
        self.time_label = QLabel("hr:min:sec:frm / 00:00:00:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        time_label_layout.addWidget(self.time_label)
        layout.addLayout(time_label_layout)

        # --- Video Navigation ---
        nav_layout = QHBoxLayout()

        # Left
        left_nav = QHBoxLayout()
        self.add_mark_button = QPushButton("Start Mark")
        self.add_mark_button.setFixedWidth(80)
        left_nav.addWidget(self.add_mark_button)
        left_nav.addStretch()

        # Center
        center_nav = QHBoxLayout()
        self.step_back_button = QPushButton("Step Back")
        self.step_back_button.setFixedWidth(80)
        center_nav.addWidget(self.step_back_button)
        self.play_button = QPushButton("Play")
        self.play_button.setFixedWidth(80)
        center_nav.addWidget(self.play_button)
        self.step_forward_button = QPushButton("Step Forward")
        self.step_forward_button.setFixedWidth(80)
        center_nav.addWidget(self.step_forward_button)

        # Right
        right_nav = QHBoxLayout()
        right_nav.addStretch()
        speed_label = QLabel("Speed:")
        right_nav.addWidget(speed_label)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "0.75x", "1x", "1.25x", "1.5x", "2x", "10x"])
        self.speed_combo.setCurrentText("1x")
        self.speed_combo.setFixedWidth(70)
        right_nav.addWidget(self.speed_combo)
        step_label = QLabel("Step Size:")
        right_nav.addWidget(step_label)
        self.step_combo = QComboBox()
        self.step_combo.addItems(["1f", "5f", "1s", "5s"])
        self.step_combo.setCurrentText("1s")
        self.step_combo.setFixedWidth(40)
        right_nav.addWidget(self.step_combo)

        nav_layout.addLayout(left_nav, stretch=1)
        nav_layout.addLayout(center_nav, stretch=0)
        nav_layout.addLayout(right_nav, stretch=1)

        layout.addLayout(nav_layout)

        # --- Trimming ---
        trim_layout = QHBoxLayout()
        
        # Left
        left_trim = QHBoxLayout()
        self.get_trim_button = QPushButton("Get Trim") 
        self.get_trim_button.setFixedWidth(80)
        left_trim.addWidget(self.get_trim_button)
        self.trim_box = QLineEdit("0")
        self.trim_box.setValidator(QIntValidator(bottom=0))
        self.trim_box.setFixedWidth(80)
        left_trim.addWidget(self.trim_box)
        left_trim.addStretch()

        # Center
        center_trim = QHBoxLayout()
        self.set_trim_button = QPushButton("Set Trim")
        self.set_trim_button.setFixedWidth(80)
        center_trim.addWidget(self.set_trim_button)
        self.trim_label = QLabel("No trim set")
        self.trim_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_trim.addWidget(self.trim_label)
        self.clear_trim_button = QPushButton("Clear Trim")
        self.clear_trim_button.setFixedWidth(80)
        center_trim.addWidget(self.clear_trim_button)

        # Right
        right_trim = QHBoxLayout()
        right_trim.addStretch()
        self.lock_trim_cbox = QCheckBox("Lock Trim")
        right_trim.addWidget(self.lock_trim_cbox)

        trim_layout.addLayout(left_trim, stretch=1)
        trim_layout.addLayout(center_trim, stretch=0)
        trim_layout.addLayout(right_trim, stretch=-1)
        layout.addLayout(trim_layout)
        
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.add_mark_button.clicked.connect(self.add_mark)
        self.step_back_button.clicked.connect(self.step_backward)
        self.step_forward_button.clicked.connect(self.step_forward)
        self.set_trim_button.clicked.connect(lambda: self.set_trim())
        self.clear_trim_button.clicked.connect(self.clear_trim)
        self.get_trim_button.clicked.connect(self.get_trim)

        self.player.playbackStateChanged.connect(self._update_button)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.positionChanged.connect(self.comment_strip.set_position)
        self.player.durationChanged.connect(self.comment_strip.set_duration)
        self.comment_strip.markerClicked.connect(self._on_marker_clicked)
        self.scrubber.sliderMoved.connect(self._on_scrubber_moved)
        self.scrubber.sliderPressed.connect(self._on_scrubber_pressed)
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)
        self.lock_trim_cbox.toggled.connect(lambda checked: self.set_trim_button.setEnabled(not checked))
        self.lock_trim_cbox.toggled.connect(lambda checked: self.clear_trim_button.setEnabled(not checked))
        self.lock_trim_cbox.toggled.connect(lambda checked: self.trim_box.setEnabled(not checked))
        self.trim_box.editingFinished.connect(
            lambda: self.set_trim(int(self.trim_box.text()))
        )

        self._controls = [
            self.set_trim_button,
            self.clear_trim_button,
            self.get_trim_button,
            self.step_back_button,
            self.step_forward_button,
            self.play_button,
            self.add_mark_button,
            self.speed_combo,
            self.step_combo,
            self.lock_trim_cbox,
            self.trim_box
        ]

        for control in self._controls:
            control.setEnabled(False)

    def _on_speed_changed(self, text):
        speed = float(text.replace("x", ""))
        self.player.setPlaybackRate(speed)

    def _calculate_step(self) -> int:
        text = self.step_combo.currentText()
        value = int(text[:-1])
        unit = text[-1]

        if unit == "f":
            return int(value * (1000/self.fps)) 
        elif unit == "s":
            return value * 1000

    def _ms_to_timecode(self, ms: int) -> tuple[int, int, int, int]:
        """
        Convert milliseconds to a time code tuple.

        Args:
            ms:  Time in milliseconds
        Returns:
            Tuple of (hours, minutes, seconds, frames)
        """
        total_seconds, remaining_ms = divmod(ms, 1000)
        frames = int(remaining_ms / 1000 * self.fps)

        total_minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(total_minutes, 60)

        return (int(hours), int(minutes), int(seconds), frames)

    def _fmt_timecode(self, timecode: tuple[int, int, int, int]) -> str:
        return "{:02d}:{:02d}:{:02d}:{:02d}".format(*timecode)

    def step_backward(self):
        step = self._calculate_step()
        self.player.setPosition(max(self.trim_start_ms, self.player.position() - step))
    
    def step_forward(self):
        step = self._calculate_step() 
        self.player.setPosition(min(self.player.position() + step, self.player.duration()))

    def set_trim(self, set_to: int | None = None):
        if set_to is None:
            self.trim_start_ms = self.player.position()
        else:
            self.trim_start_ms = set_to

        self.time_keeper.set_trim(self.trim_start_ms)
        timecode =  self._fmt_timecode(self._ms_to_timecode(self.trim_start_ms))
        self.trim_label.setText(timecode)
        self.scrubber.setRange(self.trim_start_ms, self.player.duration())
        if self.player.position() < self.trim_start_ms:
            self.player.setPosition(self.trim_start_ms)

    def clear_trim(self):
        """Remove the trim-in point and restore full range."""
        self.trim_start_ms = 0
        self.time_keeper.set_trim(self.trim_start_ms)
        self.trim_box.setText("0")
        self.trim_label.setText(f"No trim set")
        self.scrubber.setRange(0, self.player.duration())

    def get_trim(self):
        print(self.trim_start_ms)

    def load_video(self, file_path):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(file_path))
        QTimer.singleShot(0, self.player.pause)

        self.player.mediaStatusChanged.connect(self._on_media_loaded, Qt.SingleShotConnection)

        for control in self._controls:
            control.setEnabled(True)

    def _on_media_loaded(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            metadata = self.player.metaData()
            self.fps = metadata.value(QMediaMetaData.VideoFrameRate)
            self.trim_box.validator().setTop(metadata.value(QMediaMetaData.Duration))

            self.total_duration = self._ms_to_timecode(self.player.duration())
            total_duration_time_code = self._fmt_timecode(self.total_duration)
            self.time_label.setText(f"00:00:00:00 / {total_duration_time_code}")

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def toggle_play_pause(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def add_mark(self):
        self.start_mark_set = self.span_keeper.span_mark(self.player.position())
        self.scrubber.update()
        if self.start_mark_set:
            self.add_mark_button.setText("End Mark")
        else:
            self.add_mark_button.setText("Start Mark")

    def _update_button(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

    def _on_position_changed(self, position):
        # Block signals to prevent seek loop while updating slider position
        current_timecode =  self._fmt_timecode(self._ms_to_timecode(position))
        total_duration_time_code = self._fmt_timecode(self.total_duration)
        self.time_label.setText(f"{current_timecode} / {total_duration_time_code}")
        self.scrubber.blockSignals(True)
        self.scrubber.setValue(position)
        self.scrubber.blockSignals(False)

    def _on_duration_changed(self, duration):
        self.scrubber.setRange(0, duration)

    def _on_scrubber_moved(self, position):
        self.player.setPosition(position)

    def _on_scrubber_pressed(self):
        self.player.setPosition(self.scrubber.value())

    def set_comments(self, comments):
        if hasattr(self, "comment_strip"):
            self.comment_strip.set_comments(comments)

        if hasattr(self, "scrubber") and hasattr(self.scrubber, "set_comments"):
            self.scrubber.set_comments([])

    def _on_marker_clicked(self, index: int, timestamp_ms: int):
        self.player.setPosition(timestamp_ms)
        self.commentClicked.emit(index, timestamp_ms)