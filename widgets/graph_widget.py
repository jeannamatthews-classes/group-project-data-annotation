from PySide6.QtCore import (
    QPoint
)
from PySide6.QtGui import (
    Qt, QPixmap, QPainter, QPen, QPaintEvent, QResizeEvent
)
from PySide6.QtWidgets import (
    QWidget
)

class Graph(QWidget):
    """
    A widget for drawing a series of data points to the screen on a scalable graph.
    """
    def __init__(self, title: str | None = None):
        super().__init__()

        self.setMinimumSize(150, 60)

        self._title: str = title
        self._pixmap: QPixmap = QPixmap(self.size())
        self._prev_point: QPoint

        self._render_hints: int = (
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.TextAntialiasing
        )
        self._major_gridlines: bool = True
        self._minor_gridlines: bool = True # TODO: change to enum; 0 = none, 1 = major, 2 = both

        self._range: tuple[int, int] = -32768, 32768 # should be one of the following forms: [-x, x], [0, x], [-x, 0]
        self._major_resolution: QPoint = QPoint(10, 4) # number of sections
        self._minor_resolution: QPoint = QPoint(4, 2) # TODO: Auto scale as size dependent

        # Size dependent variables
        self._margin: QPoint # TODO: change to 4 value type
        self._y_scale: float
        self._point_spacing: int

        self._update_dependent_vars()
        self.clear()

    @property
    def range(self) -> tuple[int, int]:
        return self._range

    @range.setter
    def range(self, value: tuple[int, int]):
        if value == [0, 0]: # raise exceptions?
            return
        elif value[0] >= value[1]:
            return
        elif value[0] > 0 and value[1] == 0:
            value = [value[1], value[0]]
        elif value[0] < 0 and value[1] > 0: # makes symmetrical y axis
            value[1] = (max(-value[0], value[1]))
            value[0] = -value[1]

        self._range = value

        self._update_dependent_vars()
        self.clear()

    # Pass None to leave unchanged
    def set_gridlines(self, major: bool, minor: bool):
        if major is not None:
            self._major_gridlines = major
        if minor is not None:
            self._minor_gridlines = minor

        if minor == True: # major must be on with minor
            self._major_gridlines = True

        self.update()

    def draw_point(self, x: int, y: int):
        painter = self._make_painter(QPen(Qt.black, 2))

        painter.drawEllipse(x - 1, y - 1, 2, 2) # offset by radius in order to center at desired point

        painter.end()
        self.update()

    # Overload for QPoint?
    def draw_line(self, x1: int, y1: int, x2: int, y2: int, stroke: float | None = 1):
        painter = self._make_painter(QPen(Qt.black, stroke))

        painter.drawLine(x1, y1, x2, y2)

        painter.end()
        self.update()

    # TODO align modes
    def draw_text(self, x: int, y: int, text: str):
        painter = self._make_painter()

        painter.drawText(x, y, text)

        painter.end()
        self.update()

    def draw_next(self, row: list):
        y = self._y_translate(row[0])

        if self._prev_point:
            x = self._prev_point.x() + self._point_spacing
            self.draw_line(self._prev_point.x(), self._prev_point.y(), x, y)
        else:
            x = self._margin.x()

        self.draw_point(x, y)

        self._prev_point = QPoint(x, y)

    # Proof of concept
    def x_scroll(self):
        if not self._prev_point:
            return

        boundary = self._pixmap.rect().adjusted(self._margin.x() - 4, self._margin.y(), 0, 0)
        self._pixmap.scroll(-self._point_spacing * 5, 0, boundary)
        self._prev_point -= QPoint(self._point_spacing * 5, 0)

        if self._prev_point.x() < self._margin.x():
            self._prev_point = None

        self.update()

    def clear(self):
        self._pixmap.fill(Qt.white)
        self._prev_point = None

        self._draw_axes()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._pixmap)

    def resizeEvent(self, event: QResizeEvent): # FIXME: redraw with new scale instead of clear
        self._pixmap = QPixmap(event.size())

        self._update_dependent_vars()
        self.clear()

    def _update_dependent_vars(self):
        longer_range = self.range[0] if self.range[0] != 0 else self.range[1]
        self._margin = QPoint((len(str(longer_range)) * 8) + 5, 17)

        range_span = abs(self._range[0]) + abs(self._range[1])
        available_height = self.height() - (2 * self._margin.y())
        self._y_scale = 1 / (range_span / available_height)

        available_width = self.width() - self._margin.x()
        grid_spacing = available_width / self._major_resolution.x()
        self._point_spacing = grid_spacing / 10

    def _make_painter(self, pen: QPen | None = QPen(Qt.black, 1)) -> QPainter:
        painter = QPainter(self._pixmap)
        painter.setRenderHints(self._render_hints)
        painter.setPen(pen)
        return painter

    def _y_translate(self, y: int) -> int:
        return self.height() - self._margin.y() - ((y - self._range[0]) * self._y_scale)

    def _draw_axes(self):
        graph_bottom = self.height() - self._margin.y()

        # title
        if self._title:
            self.draw_text(self.width() // 2, self._margin.y() - 4, self._title)

        # x axis
        val = 0
        val_increment = 1 # TODO: scale to be accurate

        for i in range(0, self._major_resolution.x() + 1):
            x = self._margin.x() + (val * 10 * self._point_spacing)

            self.draw_text(x - 4, self.height() - 3, str(int(val))) # TODO: horizontally center at point
            if self._major_gridlines or i == 0:
                self.draw_line(x, self._margin.y(), x, graph_bottom) # FIXME: currently draws last line at last pixel; not visible
            if self._minor_gridlines:
                minor_increment = val_increment / self._minor_resolution.x()

                for _ in range(self._minor_resolution.x() - 1):
                    val += minor_increment
                    x += minor_increment * 10 * self._point_spacing
                    self.draw_line(x, self._margin.y(), x, graph_bottom, 0.5)

                val += minor_increment
            else:
                val += val_increment

        # y axis
        self.draw_line(self._margin.x(), self._margin.y(), self._margin.x(), graph_bottom)

        val = self._range[0]
        val_increment = (abs(self._range[0]) + abs(self._range[1])) / self._major_resolution.y()

        for i in range(0, self._major_resolution.y() + 1):
            y = self._y_translate(val)

            if self.range[1] - self.range[0] > 999: # only use decimals when 3 or less significant figures
                self.draw_text(2, y + 5, "{:>6d}".format(int(val)))
            else:
                self.draw_text(2, y + 5, "{:>6.1f}".format(val))

            if self._major_gridlines or i == 0:
                self.draw_line(self._margin.x(), y, self.width(), y)

            if self._minor_gridlines and i < self._major_resolution.y():
                minor_increment = val_increment / self._minor_resolution.y()

                for _ in range(self._minor_resolution.y() - 1):
                    val += minor_increment
                    y = self._y_translate(val)
                    self.draw_line(self._margin.x(), y, self.width(), y, 0.5)

                val += minor_increment
            else:
                val += val_increment