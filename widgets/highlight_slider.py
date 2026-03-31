from PySide6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt
from util.span_keeper import SpanKeeper

class HighlightSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, span_keeper: SpanKeeper | None = None):
        super().__init__(orientation)
        self._span_keeper = span_keeper

    def set_span_keeper(self, span_keeper: SpanKeeper):
        self._span_keeper = span_keeper
        self.update()

    def paintEvent(self, event):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)

        groove_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderGroove, self
        )
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, opt,
            QStyle.SubControl.SC_SliderHandle, self
        )
        handle_half = handle_rect.width() // 2

        groove_y = groove_rect.center().y()
        groove_height = 4
        x_start = groove_rect.x() + handle_half
        x_end = groove_rect.right() - handle_half
        x_current = handle_rect.center().x()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        # Draw unplayed portion of groove (grey)
        painter.setBrush(QColor(180, 180, 180))
        painter.drawRoundedRect(x_start, groove_y - groove_height // 2,
                                x_end - x_start, groove_height, 2, 2)

        # Draw played portion of groove (blue)
        painter.setBrush(QColor(0, 120, 215))
        painter.drawRoundedRect(x_start, groove_y - groove_height // 2,
                                x_current - x_start, groove_height, 2, 2)

        # Draw spans
        if self._span_keeper is not None and self.maximum() != 0:
            def val_to_x(value: int) -> int:
                usable_width = groove_rect.width() - handle_rect.width()
                return QStyle.sliderPositionFromValue(
                    self.minimum(),
                    self.maximum(),
                    value,
                    usable_width,
                    self.invertedAppearance()
                ) + groove_rect.x() + handle_half

            bar_height = 6

            for span in self._span_keeper.get_spans():
                start, end = span.get_start(), span.get_stop()
                x1 = val_to_x(start)
                x2 = val_to_x(end)
                painter.setBrush(QColor(255, 165, 0, 180))
                painter.drawRect(x1, groove_y - bar_height // 2, x2 - x1, bar_height)

            if self._span_keeper.is_start_set():
                x1 = val_to_x(self._span_keeper.start_temp)
                x2 = val_to_x(self.value())
                painter.setBrush(QColor(255, 80, 80, 130))
                painter.drawRect(x1, groove_y - bar_height // 2, x2 - x1, bar_height)

        # Draw handle on top of everything
        opt2 = QStyleOptionSlider()
        self.initStyleOption(opt2)
        opt2.subControls = QStyle.SubControl.SC_SliderHandle
        self.style().drawComplexControl(QStyle.ComplexControl.CC_Slider, opt2, painter, self)

        painter.end()