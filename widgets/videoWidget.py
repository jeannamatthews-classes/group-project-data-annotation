from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer, Qt
from widgets.helpers.highlight_slider import HighlightSlider
from timeKeeper import TimeKeeper
from backend.span_keeper import SpanKeeper

class VideoWidget(QWidget):
    def __init__(self, span_keeper: SpanKeeper, time_keeper: TimeKeeper | None = None):
        super().__init__()
        self.time_keeper = time_keeper
        self.span_keeper = span_keeper
        self.start_mark_set = False
        self._create_ui()
        
    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        self.player = QMediaPlayer()
        self.time_keeper.set_player(self.player)
        self.player.setVideoOutput(self.video_widget)
        
        self.scrubber = self.scrubber = HighlightSlider(Qt.Orientation.Horizontal, self.span_keeper)
        self.scrubber.setRange(0, 0)
        layout.addWidget(self.scrubber)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.play_button = QPushButton("Play")
        self.play_button.setFixedWidth(80)
        button_layout.addWidget(self.play_button)
        self.add_mark_button = QPushButton("Start Mark")
        self.add_mark_button.setFixedWidth(80)
        button_layout.addWidget(self.add_mark_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.play_button.clicked.connect(self.toggle_play_pause)
        self.player.playbackStateChanged.connect(self._update_button)
        self.add_mark_button.clicked.connect(self.add_mark)
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.scrubber.sliderMoved.connect(self._on_scrubber_moved)
        self.scrubber.sliderPressed.connect(self._on_scrubber_pressed)

    def load_video(self, file_path):
        self.player.stop()  
        self.player.setSource(QUrl.fromLocalFile(file_path))
        QTimer.singleShot(0, self.player.pause)

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
        self.scrubber.blockSignals(True)
        self.scrubber.setValue(position)
        self.scrubber.blockSignals(False)

    def _on_duration_changed(self, duration):
        self.scrubber.setRange(0, duration)

    def _on_scrubber_moved(self, position):
        self.player.setPosition(position)

    def _on_scrubber_pressed(self):
        self.player.setPosition(self.scrubber.value())