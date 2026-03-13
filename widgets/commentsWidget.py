from dataclasses import dataclass
from typing import Optional, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QCheckBox,
)


@dataclass
class CommentEntry:
    timestamp_ms: int
    data_point: str
    comment: str


def format_ms(ms: int) -> str:
    total_seconds = max(0, ms // 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"


class CommentWidget(QWidget):
    jumpRequested = Signal(int)  # timestamp in ms

    def __init__(self):
        super().__init__()
        self.current_timestamp_ms = 0
        self.comments: List[CommentEntry] = []
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Comments")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #222; color: white; padding: 6px;")
        layout.addWidget(title)

        self.timestamp_label = QLabel("Current video time: 00:00")
        layout.addWidget(self.timestamp_label)

        self.use_current_time_checkbox = QCheckBox("Use current video time")
        self.use_current_time_checkbox.setChecked(True)
        layout.addWidget(self.use_current_time_checkbox)

        timestamp_row = QHBoxLayout()
        timestamp_row.addWidget(QLabel("Timestamp (ms):"))
        self.timestamp_input = QLineEdit()
        self.timestamp_input.setPlaceholderText("Auto-filled from video")
        self.timestamp_input.setEnabled(False)
        timestamp_row.addWidget(self.timestamp_input)
        layout.addLayout(timestamp_row)

        self.use_current_time_checkbox.toggled.connect(self._on_time_mode_changed)

        data_row = QHBoxLayout()
        data_row.addWidget(QLabel("Data point:"))
        self.data_point_input = QLineEdit()
        self.data_point_input.setPlaceholderText("Optional: CSV value / label / row id")
        data_row.addWidget(self.data_point_input)
        layout.addLayout(data_row)

        layout.addWidget(QLabel("Comment text:"))
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter your annotation here...")
        self.comment_input.setFixedHeight(120)
        layout.addWidget(self.comment_input)

        button_row = QHBoxLayout()
        self.add_button = QPushButton("Add Comment")
        self.clear_button = QPushButton("Clear Inputs")
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)

        self.add_button.clicked.connect(self.add_comment)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.comment_list.itemDoubleClicked.connect(self._jump_to_comment)

    def _on_time_mode_changed(self, checked: bool):
        self.timestamp_input.setEnabled(not checked)
        if checked:
            self.timestamp_input.clear()

    def set_current_timestamp(self, timestamp_ms: int):
        self.current_timestamp_ms = timestamp_ms
        self.timestamp_label.setText(f"Current video time: {format_ms(timestamp_ms)}")

    def add_comment(self):
        comment_text = self.comment_input.toPlainText().strip()
        data_point = self.data_point_input.text().strip()

        if not comment_text:
            QMessageBox.warning(self, "Missing Comment", "Please enter comment text.")
            return

        if self.use_current_time_checkbox.isChecked():
            timestamp_ms = self.current_timestamp_ms
        else:
            raw = self.timestamp_input.text().strip()
            if not raw.isdigit():
                QMessageBox.warning(
                    self,
                    "Invalid Timestamp",
                    "Timestamp must be an integer number of milliseconds.",
                )
                return
            timestamp_ms = int(raw)

        entry = CommentEntry(
            timestamp_ms=timestamp_ms,
            data_point=data_point,
            comment=comment_text,
        )
        self.comments.append(entry)
        self._add_list_item(entry)
        self.comment_input.clear()
        self.data_point_input.clear()

    def _add_list_item(self, entry: CommentEntry):
        header = format_ms(entry.timestamp_ms)
        if entry.data_point:
            header += f" | {entry.data_point}"

        preview = entry.comment.replace("\n", " ")
        if len(preview) > 60:
            preview = preview[:57] + "..."

        item_text = f"{header}\n{preview}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, entry.timestamp_ms)
        self.comment_list.addItem(item)

    def _jump_to_comment(self, item: QListWidgetItem):
        timestamp_ms = item.data(Qt.UserRole)
        if isinstance(timestamp_ms, int):
            self.jumpRequested.emit(timestamp_ms)

    def clear_inputs(self):
        self.timestamp_input.clear()
        self.data_point_input.clear()
        self.comment_input.clear()

    def get_comments(self) -> List[CommentEntry]:
        return self.comments