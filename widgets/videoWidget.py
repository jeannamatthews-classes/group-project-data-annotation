from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, QTimer
import time

class VideoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)

        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        
        self.play_button = QPushButton("Play")
        layout.addWidget(self.play_button)

        self.play_button.clicked.connect(self.toggle_play_pause)
        self.player.playbackStateChanged.connect(self._update_button)

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