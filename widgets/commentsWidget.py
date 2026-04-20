from typing import Optional, List
import qtawesome as qta

from PySide6.QtCore import Qt, Signal, QRegularExpression
from PySide6.QtGui import QAction, QRegularExpressionValidator
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
RASS = ['', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4']


class CommentWidget(QWidget):
    jumpRequested = Signal(int)  # timestamp in ms

    def __init__(self, timekeeper: TimeKeeper):
        super().__init__()
        self.time_keeper = timekeeper
        self.current_timestamp_ms = 0

        self.comment_list = QListWidget()
        self.comment_keeper = CommentKeeper(self.comment_list)

        # Setup Time Validators
        self.time_rx = QRegularExpression(r"^(\d+:)?([0-5]\d):([0-5]\d)$")

        self._create_ui()

        # Conenct to singals
        self.time_keeper.positionChanged.connect(self._on_position_changed)
        self.comment_keeper.selected_comment_changed.connect(self._on_comment_changed)

    def _create_ui(self):
        layout = QVBoxLayout(self)

        self.title = QLabel("Add Comment")
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
        self.start_time_input.setValidator(
            QRegularExpressionValidator(self.time_rx, self.start_time_input))
        self.start_time_input.editingFinished.connect(self._user_fill_starttime)
        self.start_time_action.triggered.connect(self._start_use_current_time)
        self.start_time_input.addAction(self.start_time_action, QLineEdit.ActionPosition.TrailingPosition)
        start_time_row.addWidget(self.start_time_input)
        self.start_time_input.setMaximumWidth(200)
        layout.addLayout(start_time_row)

        # End Time Field
        end_time_row = QHBoxLayout()
        end_time_row.addWidget(QLabel("End Time"))
        self.end_time_input = QLineEdit()
        self.end_time_input.setValidator(
            QRegularExpressionValidator(self.time_rx, self.end_time_input))
        self.end_time_input.editingFinished.connect(self._user_fill_endtime)
        self.end_time_action.triggered.connect(self._end_use_current_time)
        self.end_time_input.addAction(self.end_time_action, QLineEdit.ActionPosition.TrailingPosition)
        end_time_row.addWidget(self.end_time_input)
        self.end_time_input.setMaximumWidth(200)
        layout.addLayout(end_time_row)

        # Sidedness
        side_row = QHBoxLayout()
        side_row.addWidget(QLabel("Sidedness:"))
        self.side_input = QLineEdit()
        side_row.addWidget(self.side_input)
        self.side_input.setMaximumWidth(200)
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
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumSize(100, 25)
        self.new_button = QPushButton("New")
        self.new_button.setMinimumSize(100, 25)
        self.delete_button = QPushButton("Delete")
        self.delete_button.setMinimumSize(100, 25)

        button_row.addWidget(self.save_button)
        button_row.addWidget(self.new_button)
        button_row.addWidget(self.delete_button)
        layout.addLayout(button_row)

        self.save_button.clicked.connect(self._save_comment)
        self.new_button.clicked.connect(self._select_empty)
        self.delete_button.clicked.connect(self.comment_keeper.delete_current_comment)
        self.comment_input.textChanged.connect(self._update_comment)


        # Comments UI
        layout.addWidget(QLabel("Saved comments:"))
        layout.addWidget(self.comment_list, stretch=1)

    def _on_comment_changed(self, index):
        # Write all fields to match new comment
        if index == -1:
            self.title.setText("New Comment")
            self.save_button.setText("Add")
            self.clear_inputs()
        else:
            self.start_time_input.setText(format_ms(self.comment_keeper.selected.start_time_ms))
            self.end_time_input.setText(format_ms(self.comment_keeper.selected.end_time_ms))
            self.side_input.setText(self.comment_keeper.selected.side)

            # Combo Boxes
            index = self.rass_box.findText(self.comment_keeper.selected.RASS)
            if index >= 0:
                 self.rass_box.setCurrentIndex(index)

            index = self.movement_box.findText(self.comment_keeper.selected.movement)
            if index >= 0:
                 self.movement_box.setCurrentIndex(index)
            self.comment_input.setText(self.comment_keeper.selected.comment)
            self.datetime_created = self.comment_keeper.selected.datetime_created

            self.title.setText("Modify Comment") 
            self.save_button.setText("Update")

    def _select_empty(self):
        self.comment_keeper.select_comment(-1)

    def _save_comment(self):
        self.comment_keeper.working.side = self.side_input.text()
        self.comment_keeper.working.RASS = self.rass_box.currentData()
        self.comment_keeper.working.movement = self.movement_box.currentData()
        self.comment_keeper.working.comment = self.comment_input.toPlainText()
        self.comment_keeper.save_comment()

    def _update_comment(self):
        self.comment_keeper.working.comment = self.comment_input.toPlainText()

    def _on_position_changed(self, position):
        self.current_timestamp_ms = position
        self.timestamp_label.setText(f"Current video time: {format_ms(self.current_timestamp_ms)}")
        self.comment_keeper.sync_list(position)

    def _start_use_current_time(self):
        if not self.start_time_input.hasFocus():
            return
        self.comment_keeper.working.start_time_ms = self.current_timestamp_ms
        self.start_time_input.setText(format_ms(self.current_timestamp_ms))

    def _end_use_current_time(self):
        if not self.end_time_input.hasFocus():
            return
        self.comment_keeper.working.end_time_ms = int(self.time_keeper.time)
        self.end_time_input.setText(format_ms(self.current_timestamp_ms))

    def _user_fill_starttime(self):
        self.comment_keeper.working.start_time_ms = to_ms(self.start_time_input.text())

    def _user_fill_endtime(self):
        self.comment_keeper.working.end_time_ms_time_ms = to_ms(self.end_time_input.text())

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