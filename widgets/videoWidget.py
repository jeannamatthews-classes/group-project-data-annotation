from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QLabel
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer, Qt
from widgets.highlight_slider import HighlightSlider
from timeKeeper import TimeKeeper
from util.span_keeper import SpanKeeper

class VideoWidget(QWidget):
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



        self.play_button.clicked.connect(self.toggle_play_pause)
        self.add_mark_button.clicked.connect(self.add_mark)
        self.step_back_button.clicked.connect(self.step_backward)
        self.step_forward_button.clicked.connect(self.step_forward)

        self.player.playbackStateChanged.connect(self._update_button)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.scrubber.sliderMoved.connect(self._on_scrubber_moved)
        self.scrubber.sliderPressed.connect(self._on_scrubber_pressed)
        self.speed_combo.currentTextChanged.connect(self._on_speed_changed)

        self._controls = [
            self.step_back_button,
            self.step_forward_button,
            self.play_button,
            self.add_mark_button,
            self.speed_combo,
            self.step_combo,
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
        if self.trim_start_ms < self.player.position() - step < self.player.duration():
            self.player.setPosition(self.player.position() - step)    
    
    def step_forward(self):
        step = self._calculate_step() 
        if self.trim_start_ms < self.player.position() + step < self.player.duration():
            self.player.setPosition(self.player.position() + step)


    def load_video(self, file_path):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(file_path))
        QTimer.singleShot(0, self.player.pause)

        import cv2
        cap = cv2.VideoCapture(file_path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()

        self.player.mediaStatusChanged.connect(self._on_media_loaded)

        for control in self._controls:
            control.setEnabled(True)

    def _on_media_loaded(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.player.mediaStatusChanged.disconnect(self._on_media_loaded)

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
        self.time_label.setText(f"{current_timecode}/ {total_duration_time_code}")
        self.scrubber.blockSignals(True)
        self.scrubber.setValue(position)
        self.scrubber.blockSignals(False)

    def _on_duration_changed(self, duration):
        self.scrubber.setRange(0, duration)

    def _on_scrubber_moved(self, position):
        self.player.setPosition(position)

    def _on_scrubber_pressed(self):
        self.player.setPosition(self.scrubber.value())