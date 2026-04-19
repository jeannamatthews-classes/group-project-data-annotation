from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtCore import QObject, Signal, QUrl


class TimeKeeper(QObject):

    # Create Signals
    sourceChanged = Signal(QUrl)        # Emits the QUrl of the video source
    positionChanged = Signal(int)       # Emits the current position of the video in milliseconds
    windowChanged = Signal(int, int)    # Emits the start and end of the current window in milliseconds

    def __init__(self):
        super().__init__()
        self.time = 0
        self.trim = 0
        self.windowSize = 0
        self.windowStart = 0
        self.windowEnd = 0

    def set_trim(self, trim: int):
        self.trim = trim

    def set_player(self, player: QMediaPlayer):
        self.player = player
        self.player.sourceChanged.connect(self._on_sourceChanged)
        self.player.positionChanged.connect(self._on_positionChanged)

    # Update Window off current center
    def set_window_size(self, size):
        self.windowSize = size
        self.windowChanged.emit(self.windowStart, self.windowEnd)
        midpoint = (self.windowEnd - self.windowStart) / 2 + self.windowStart
        windowStart = midpoint - self.windowSize / 2

        # Prevent window from going negative
        if windowStart < 0:
            self.windowStart = 0
            self.windowEnd = self.windowSize
        else:
            self.windowStart = windowStart
            self.windowEnd = midpoint + self.windowSize / 2

    def get_time(self):
        return self.time

    def get_trim(self):
        return self.trim

    def get_window_size(self):
        return self.windowSize

    def get_window_start(self):
        return self.windowStart

    def get_window_end(self):
        return self.windowEnd

    def _on_sourceChanged(self, source):
        self._on_positionChanged(0)
        self.sourceChanged.emit(source)

    def _on_positionChanged(self, position):
        self.time = position - self.trim
        self.positionChanged.emit(position - self.trim)