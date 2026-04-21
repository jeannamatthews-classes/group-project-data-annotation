from collections import defaultdict

from PySide6.QtCore import QPointF, Signal, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class CommentMarkerStrip(QWidget):
    markerClicked = Signal(int, int)  # index, timestamp_ms

    def __init__(self, parent=None):
        super().__init__(parent)
        self._comments = []
        self._position_ms = 0
        self._duration_ms = 1
        self._marker_positions = []

        self.setFixedHeight(18)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_comments(self, comments):
        self._comments = list(comments)
        self.update()

    def set_position(self, position_ms: int):
        self._position_ms = position_ms
        self.update()

    def set_duration(self, duration_ms: int):
        self._duration_ms = max(1, duration_ms)
        self.update()

    def _x_from_ms(self, ms: int) -> float:
        left = 10
        right = self.width() - 10
        usable = max(1, right - left)
        return left + (ms / self._duration_ms) * usable

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        self._marker_positions.clear()

        if not self._comments:
            return

        y = self.height() - 6
        buckets = defaultdict(list)

        for i, comment in enumerate(self._comments):
            x = self._x_from_ms(comment.start_time_ms)
            buckets[round(x)].append((i, comment))

        for x, entries in buckets.items():
            active = any(
                entry.start_time_ms <= self._position_ms <= entry.end_time_ms
                for _, entry in entries
            )

            radius = 7 if active else 5

            painter.setPen(QPen(QColor(200, 60, 60), 1.5))
            painter.setBrush(
                QColor(255, 230, 230) if active else QColor(255, 255, 255)
            )
            painter.drawEllipse(QPointF(x, y), radius, radius)

            first_index, first_comment = entries[0]
            self._marker_positions.append((x, first_index))

            if len(entries) > 1:
                painter.drawText(int(x - radius), int(y + 4), str(len(entries)))

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        click_x = event.position().x()
        threshold = 10

        closest_index = None
        closest_dist = None

        for x, index in self._marker_positions:
            dist = abs(click_x - x)
            if dist <= threshold and (closest_dist is None or dist < closest_dist):
                closest_dist = dist
                closest_index = index

        if closest_index is not None:
            comment = self._comments[closest_index]
            self.markerClicked.emit(closest_index, comment.start_time_ms)