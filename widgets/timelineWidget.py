from PySide6.QtGui import (
    Qt, QMouseEvent
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout
)

from util.csv_reader import CSVReader
from widgets.graph_widget import Graph

class TimelineWidget(QWidget):
    def __init__(self, datapath: str | None = None, title: str | None = None):
        super().__init__()

        self.data = CSVReader(datapath)
        self.graph = Graph(title)

        self._create_ui()

        # self._total_time()
        # self._data_stats(1, 15)
        # self._calculate_freq()

    def _create_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.graph)
        self.setLayout(layout)

    def load_data(self, datapath: str):
        del self.data
        self.data = CSVReader(datapath)
        self.graph.clear()

    def connect_signals(self, time_keeper):
        time_keeper.positionChanged.connect(self._on_position_changed)
        time_keeper.windowChanged.connect(self._on_window_changed)

    def _on_position_changed(self, position):
        pass

    def _on_window_changed(self, start, end):
        pass
    # temporary development usage
    def mousePressEvent(self, event: QMouseEvent):
        match(event.button()):
            case Qt.LeftButton:
                if self.data.success:
                    for _ in range(5):
                        self.graph.draw_next(self.data.next_row())
            case Qt.RightButton:
                self.graph.clear()
                self.data.reset()
            case Qt.MiddleButton:
                self.graph.x_scroll()

    # development helpers / data analysis
    def _total_time(self):
        end = 0

        start = self.data.next_row()[self.data.time_idx]
        row = self.data.next_row()
        while row:
            end = row[self.data.time_idx]
            row = self.data.next_row()

        dt = end - start

        print("\nTotal time:")
        print(f"  {dt} ms")

        print(f"  {dt / 1000 // 3600:.0f} hour", end=" ")
        print(f"{dt / 1000 % 3600 // 60:.0f} min", end=" ")
        print(f"{dt / 1000 % 60 // 1:.0f} sec", end=" ")
        print(f"{dt % 1000:.0f} ms\n")
        self.data.reset()

    def _data_stats(self, start_col: int, end_col: int):
        print("Data range:")
        print(f"   Col\t\t{'Min':^10s}\t{'Avg':^10s}\t{'Max':^10s}")

        cols = end_col - start_col + 1

        mins = [float("inf")] * (cols)
        maxs = [float("-inf")] * (cols)
        sums = [0] * (cols)
        count = 0

        row = self.data.next_row()
        while row:
            count += 1
            vals = row[start_col - 1:end_col]
            for i in range(cols):
                mins[i] = min(mins[i], vals[i])
                maxs[i] = max(maxs[i], vals[i])
                sums[i] += vals[i]
            row = self.data.next_row()

        for i in range(cols):
            print(f"  {i + start_col:3d}  |\t{mins[i]:< 10.2f}\t{sums[i] / count:< 11.3f}\t{maxs[i]:< 10.2f}")
        self.data.reset()

    def _calculate_freq(self):
        sum = 0
        time = self.data.next_row()[self.data._time_idx]

        i = 0
        row = self.data.next_row()
        while row:
            i += 1
            next_time = row[self.data._time_idx]

            sum += next_time - time
            time = next_time
            row = self.data.next_row()

        if i != 0:
            print("\nCalculated frequency:")
            print(f"  {sum / i:.3f} ms average = {1000 / (sum / i)} Hz")
        self.data.reset()
