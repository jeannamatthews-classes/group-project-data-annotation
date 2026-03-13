from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSlider
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer, Qt

class VideoWidget(QWidget):
    positionUpdated = Signal(int)  # Signal to emit the current position in milliseconds
    durationUpdated = Signal(int)  # Signal to emit the duration in milliseconds

    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        
        self.scrubber = QSlider(Qt.Orientation.Horizontal)
        self.scrubber.setRange(0, 0)
        layout.addWidget(self.scrubber)
        
        self.play_button = QPushButton("Play")
        layout.addWidget(self.play_button)

        self.play_button.clicked.connect(self.toggle_play_pause)
        self.player.playbackStateChanged.connect(self._update_button)

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