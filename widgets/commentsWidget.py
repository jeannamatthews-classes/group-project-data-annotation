from typing import Optional, List
import qtawesome as qta

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QComboBox,
    QListWidgetItem,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMessageBox,
)

from timeKeeper import TimeKeeper
from util.comment_keeper import CommentKeeper, CommentEntry, format_ms

MOVEMENTS = ["", "Up", "Down", "Left", "Right"]
RASS = ['', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4']


class CommentWidget(QWidget):
    jumpRequested = Signal(int)  # timestamp in ms

    def __init__(self, timekeeper: TimeKeeper):
        super().__init__()
        self.time_keeper = timekeeper
        self.current_timestamp_ms = 0

        self.comment_list = QListWidget()
        self.comment_keeper = CommentKeeper(self.comment_list)
        self._create_ui()

        # Conenct to singals
        self.time_keeper.positionChanged.connect(self._on_position_changed)
        self.comment_keeper.selected_comment_changed.connect(self._on_comment_changed)

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.title = QLabel("Comments")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("background-color: #222; color: white; padding: 6px;")
        layout.addWidget(self.title)

        self.timestamp_label = QLabel("Current video time: 00:00")
        layout.addWidget(self.timestamp_label)


        # Start and End Time Fields
        # Create Icon
        icon = qta.icon('ei.time', color='gray')

        # Setup Icon Actions
        self.start_time_action = QAction(icon, "Use Current Time", self)
        self.end_time_action = QAction(icon, "Use Current Time", self)

        # Start Time Field
        start_time_row = QHBoxLayout()
        start_time_row.addWidget(QLabel("Start Time"))
        self.start_time_input = QLineEdit()
        self.start_time_action.triggered.connect(self._start_use_current_time)
        self.start_time_input.addAction(self.start_time_action, QLineEdit.ActionPosition.TrailingPosition)
        start_time_row.addWidget(self.start_time_input)
        layout.addLayout(start_time_row)

        # End Time Field
        end_time_row = QHBoxLayout()
        end_time_row.addWidget(QLabel("End Time"))
        self.end_time_input = QLineEdit()
        self.end_time_action.triggered.connect(self._end_use_current_time)
        self.end_time_input.addAction(self.end_time_action, QLineEdit.ActionPosition.TrailingPosition)
        end_time_row.addWidget(self.end_time_input)
        layout.addLayout(end_time_row)


        # Sidedness
        side_row = QHBoxLayout()
        side_row.addWidget(QLabel("Sidedness:"))
        self.side_input = QLineEdit()
        side_row.addWidget(self.side_input)
        layout.addLayout(side_row)

        # RASS
        rass_row = QHBoxLayout()
        rass_row.addWidget(QLabel("RASS:"))
        self.rass_box = QComboBox()
        self.rass_box.addItems((RASS))
        rass_row.addWidget(self.rass_box)
        layout.addLayout(rass_row)

        # Movement Characteristic
        movement_row = QHBoxLayout()
        movement_row.addWidget(QLabel("Movement:"))
        self.movement_box = QComboBox();
        self.movement_box.addItems(MOVEMENTS)
        movement_row.addWidget(self.movement_box)
        layout.addLayout(movement_row)

        # Comment
        layout.addWidget(QLabel("Comment text:"))
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter your annotation here...")
        self.comment_input.setFixedHeight(120)
        layout.addWidget(self.comment_input)

        # Buttons
        button_row = QHBoxLayout()
        self.save_button = QPushButton("Save Comment")
        self.clear_button = QPushButton("Clear Inputs")
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        self.save_button.clicked.connect(self.comment_keeper.save_comment)
        self.clear_button.clicked.connect(self.clear_inputs)

        # self.close_button_row = QHBoxLayout()
        self.close_button = QPushButton("Close Comment")
        # self.close_button_row.addWidget(self.save_button)
        layout.addWidget(self.close_button)

        self.close_button.clicked.connect(self.close_comment)

        # Comments UI
        layout.addWidget(QLabel("Saved comments:"))
        layout.addWidget(self.comment_list, stretch=1)

    def _on_comment_changed(self, index):
        # Write all fields to match new comment
        if index == -1:
            self.title.selectedText = "New Comment"
            self.save_button.setText("Add Comment")
            self.clear_inputs()
        else:
            self.start_time_input = self.comment_keeper.start_time_ms
            self.end_time_input = self.comment_keeper.end_time_ms
            self.side_input = self.comment_keeper.side
            self.rass_box = self.comment_keeper.rass
            self.movement_box = self.comment_keeper.movement
            self.comment_input = self.comment_keeper.comment
            self.datetime_created = self.comment_keeper.datetime_created

            self.title.selectedText = "Modify Comment"
            self.save_button.setText("Update Comment")

    def _on_position_changed(self, position):
        self.current_timestamp_ms = position
        self.timestamp_label.setText(f"Current video time: {format_ms(self.current_timestamp_ms)}")
        self.comment_keeper.sync_list(position)

    def _start_use_current_time(self):
        self.comment_keeper.selected.start_time_ms = self.current_timestamp_ms
        self.start_time_input.setText(format_ms(self.current_timestamp_ms))

    def _end_use_current_time(self):
        self.comment_keeper.selected.start_time_ms = self.time_keeper.time
        self.end_time_input.setText(format_ms(self.current_timestamp_ms))

    def _add_comment(self):
        self.comment_keeper.add_comment()
        self.clear_inputs()

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
        self.start_time_input.clear()
        self.end_time_input.clear()
        self.side_input.clear()
        self.rass_box.clear()
        self.movement_box.clear()
        self.comment_input.clear()

    def close_comment(self):
        self.comment_keeper.select_empty_comment()

    def _refresh_comments(self):

        for entry in self.comment_keeper.comments:
            display_text = f"[{entry.start_time_ms}] {entry.comment}"
            item = QListWidgetItem(display_text)
            
            # Link the object to the UI item
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.comments_list.addItem(item)