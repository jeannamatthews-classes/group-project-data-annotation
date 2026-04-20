from typing import List

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
from util.comment_keeper import CommentKeeper, CommentEntry, format_ms, to_ms

MOVEMENTS = ["", "Up", "Down", "Left", "Right"]
RASS = ["", "-5", "-4", "-3", "-2", "-1", "0", "1", "2", "3", "4"]



class CommentWidget(QWidget):
    jumpRequested = Signal(int)
    commentsChanged = Signal()

    def __init__(self, timekeeper: TimeKeeper):
        super().__init__()
        self.time_keeper = timekeeper
        self.current_timestamp_ms = 0

        self.comment_list = QListWidget()
        self.comment_keeper = CommentKeeper(self.comment_list)

        self._create_ui()

        self.time_keeper.positionChanged.connect(self._on_position_changed)
        self.comment_keeper.selected_comment_changed.connect(self._on_comment_changed)
        self.comment_list.currentRowChanged.connect(self.comment_keeper.select_comment)
        self.comment_list.itemDoubleClicked.connect(self._jump_to_comment)

        self.comment_keeper.select_empty_comment()

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.title = QLabel("New Comment")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("background-color: #222; color: white; padding: 6px;")
        layout.addWidget(self.title)

        self.timestamp_label = QLabel("Current video time: 00:00")
        layout.addWidget(self.timestamp_label)

        icon = qta.icon("ei.time", color="gray")
        self.start_time_action = QAction(icon, "Use Current Time", self)
        self.end_time_action = QAction(icon, "Use Current Time", self)

        # Start time
        start_time_row = QHBoxLayout()
        start_time_row.addWidget(QLabel("Start Time"))
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("mm:ss or hh:mm:ss")
        self.start_time_action.triggered.connect(self._start_use_current_time)
        self.start_time_input.addAction(
            self.start_time_action,
            QLineEdit.ActionPosition.TrailingPosition,
        )
        start_time_row.addWidget(self.start_time_input)
        layout.addLayout(start_time_row)

        # End time
        end_time_row = QHBoxLayout()
        end_time_row.addWidget(QLabel("End Time"))
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("mm:ss or hh:mm:ss")
        self.end_time_action.triggered.connect(self._end_use_current_time)
        self.end_time_input.addAction(
            self.end_time_action,
            QLineEdit.ActionPosition.TrailingPosition,
        )
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
        self.rass_box.addItems(RASS)
        rass_row.addWidget(self.rass_box)
        layout.addLayout(rass_row)

        # Movement
        movement_row = QHBoxLayout()
        movement_row.addWidget(QLabel("Movement:"))
        self.movement_box = QComboBox()
        self.movement_box.addItems(MOVEMENTS)
        movement_row.addWidget(self.movement_box)
        layout.addLayout(movement_row)

        # Comment text
        layout.addWidget(QLabel("Comment text:"))
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter your annotation here...")
        self.comment_input.setFixedHeight(120)
        layout.addWidget(self.comment_input)

        # Buttons
        button_row = QHBoxLayout()
        self.save_button = QPushButton("Save Comment")
        self.new_button = QPushButton("New Comment")
        self.delete_button = QPushButton("Delete Comment")

        button_row.addWidget(self.save_button)
        button_row.addWidget(self.new_button)
        button_row.addWidget(self.delete_button)
        layout.addLayout(button_row)

        self.save_button.clicked.connect(self.save_current_comment)
        self.new_button.clicked.connect(self.close_comment)
        self.delete_button.clicked.connect(self.delete_current_comment)

        # Saved comments
        layout.addWidget(QLabel("Saved comments:"))
        layout.addWidget(self.comment_list, stretch=1)

    def _on_comment_changed(self, index: int):
        if index == -1:
            self.title.setText("New Comment")
            self.save_button.setText("Save Comment")
            self.clear_inputs()
            return

        entry = self.comment_keeper.selected

        self.start_time_input.setText(format_ms(entry.start_time_ms))
        self.end_time_input.setText(format_ms(entry.end_time_ms))
        self.side_input.setText(entry.side)
        self._set_combo_text(self.rass_box, entry.RASS)
        self._set_combo_text(self.movement_box, entry.movement)
        self.comment_input.setPlainText(entry.comment)

        self.title.setText("Modify Comment")
        self.save_button.setText("Update Comment")

    def _on_position_changed(self, position: int):
        self.current_timestamp_ms = position
        self.timestamp_label.setText(
            f"Current video time: {format_ms(self.current_timestamp_ms)}"
        )
        self.comment_keeper.sync_list(position)

    def _start_use_current_time(self):
        self.start_time_input.setText(format_ms(self.current_timestamp_ms))

    def _end_use_current_time(self):
        self.end_time_input.setText(format_ms(self.current_timestamp_ms))

    def _comment_from_inputs(self) -> CommentEntry:
        comment_text = self.comment_input.toPlainText().strip()
        if not comment_text:
            raise ValueError("Please enter comment text.")

        start_text = self.start_time_input.text().strip()
        end_text = self.end_time_input.text().strip()

        start_ms = to_ms(start_text) if start_text else self.current_timestamp_ms
        end_ms = to_ms(end_text) if end_text else start_ms

        if end_ms < start_ms:
            start_ms, end_ms = end_ms, start_ms

        previous_created = self.comment_keeper.selected.datetime_created

        return CommentEntry(
            start_time_ms=start_ms,
            end_time_ms=end_ms,
            side=self.side_input.text().strip(),
            RASS=self.rass_box.currentText().strip(),
            movement=self.movement_box.currentText().strip(),
            comment=comment_text,
            datetime_created=previous_created,
        )

    def save_current_comment(self):
        try:
            entry = self._comment_from_inputs()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        self.comment_keeper.save_comment(entry)
        self.commentsChanged.emit()

    def delete_current_comment(self):
        if self.comment_keeper.selected_index == -1:
            QMessageBox.information(self, "No Comment Selected", "Select a saved comment to delete.")
            return

        self.comment_keeper.delete_current_comment()
        self.commentsChanged.emit()

    def _jump_to_comment(self, item: QListWidgetItem):
        timestamp_ms = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(timestamp_ms, int):
            self.jumpRequested.emit(timestamp_ms)

    def clear_inputs(self):
        self.start_time_input.clear()
        self.end_time_input.clear()
        self.side_input.clear()
        self.rass_box.setCurrentIndex(0)
        self.movement_box.setCurrentIndex(0)
        self.comment_input.clear()

    def close_comment(self):
        self.comment_list.clearSelection()
        self.comment_keeper.select_empty_comment()

    def _set_combo_text(self, combo: QComboBox, value: str):
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentIndex(0)

    def get_comments(self) -> List[CommentEntry]:
        return self.comment_keeper.get_comments()