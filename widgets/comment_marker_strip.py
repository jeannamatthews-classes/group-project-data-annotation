from collections import defaultdict

from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget


class CommentMarkerStrip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._comments = []
        self._position_ms = 0
        self._duration_ms = 1
        self.setFixedHeight(18)

    def set_comments(self, comments):
        self._comments = list(comments)
        self.update()

    def set_position(self, position_ms: int):
        self._position_ms = position_ms
        self.update()

    def set_duration(self, duration_ms: int):
        self._duration_ms = max(1, duration_ms)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self._comments:
            return

        left = 10
        right = self.width() - 10
        usable = max(1, right - left)
        y = self.height() // 2

        buckets = defaultdict(list)

        for comment in self._comments:
            x = left + (comment.start_time_ms / self._duration_ms) * usable
            buckets[round(x)].append(comment)

        for x, entries in buckets.items():
            active = any(
                entry.start_time_ms <= self._position_ms <= entry.end_time_ms
                for entry in entries
            )

            radius = 7 if active else 5

            painter.setPen(QPen(QColor(200, 60, 60), 1.5))
            painter.setBrush(
                QColor(255, 230, 230) if active else QColor(255, 255, 255)
            )
            painter.drawEllipse(QPointF(x, y), radius, radius)

            if len(entries) > 1:
                painter.drawText(int(x - radius), int(y + 4), str(len(entries)))