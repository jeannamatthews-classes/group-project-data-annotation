from typing import Optional, List
import qtawesome as qta
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
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

from timeKeeper import TimeKeeper
from util.comment_keeper import CommentKeeper, CommentEntry




def format_ms(ms: int) -> str:
    total_seconds = max(0, ms // 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"


class CommentWidget(QWidget):
    jumpRequested = Signal(int)# timestamp in ms
    commentsChanged = Signal()  

    def __init__(self, timekeeper: TimeKeeper):
        super().__init__()
        self.time_keeper = timekeeper
        self.current_timestamp_ms = 0
        self.comment_keeper = CommentKeeper()
        self._create_ui()

        self.time_keeper.positionChanged.connect(self._on_position_changed)

    def _create_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Comments")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background-color: #222; color: white; padding: 6px;")
        layout.addWidget(title)

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
        self.rass_input = QLineEdit()
        rass_row.addWidget(self.rass_input)
        layout.addLayout(rass_row)

        # Movement Characteristic -- TODO: Change this to a dropdown
        movement_row = QHBoxLayout()
        movement_row.addWidget(QLabel("Movement:"))
        self.movement_input = QLineEdit()
        movement_row.addWidget(self.movement_input)
        layout.addLayout(movement_row)

        # Comment
        layout.addWidget(QLabel("Comment text:"))
        self.comment_input = QTextEdit()
        self.comment_input.setPlaceholderText("Enter your annotation here...")
        self.comment_input.setFixedHeight(120)
        layout.addWidget(self.comment_input)

        # Button
        button_row = QHBoxLayout()
        self.add_button = QPushButton("Add Comment")
        self.clear_button = QPushButton("Clear Inputs")
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.clear_button)
        layout.addLayout(button_row)

        self.add_button.clicked.connect(self.add_comment)
        self.clear_button.clicked.connect(self.clear_inputs)
        
        # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)
        self.comment_list.itemDoubleClicked.connect(self._jump_to_comment)

        # Comments UI
        # self.comment_keeper.comments_ui(self.comment_keeper, layout)

    def _on_position_changed(self, position):
        self.current_timestamp_ms = position
        self.timestamp_label.setText(f"Current video time: {format_ms(self.current_timestamp_ms)}"
    )
    
    def _start_use_current_time(self):
        self.start_time_input.setText(str(self.time_keeper.get_time()))

    def _end_use_current_time(self):
        self.end_time_input.setText(str(self.time_keeper.get_time()))
    
    def add_comment(self):
         comment_text = self.comment_input.toPlainText().strip()
         #data_point = self.data_point_input.text().strip()

         if not comment_text:
             QMessageBox.warning(self, "Missing Comment", "Please enter comment text.")
             return
         
         try: 
            start_text = self.start_time_input.text().strip()
            end_text = self.end_time_input.text().strip()

            start_ms = int(start_text) if start_text else self.current_timestamp_ms
            end_ms = int(end_text) if end_text else start_ms

            if end_ms < start_ms:
                start_ms, end_ms = end_ms, start_ms

            rass_text = self.rass_input.text().strip()
            rass_value = int(rass_text) if rass_text else 0
            
         except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Start time, end time, and RASS must be integers.")
            return

         entry = CommentEntry(
                start_time_ms=start_ms,
                end_time_ms=end_ms,
                side=self.side_input.text().strip(),
                RASS=rass_value,
                movement=self.movement_input.text().strip(),
                comment=comment_text,
                #datetime_created=datetime.now().isoformat(timespec="seconds"),
            )

         self.comment_keeper.add_comment(entry)
         self._add_list_item(entry)
         self.commentsChanged.emit()
         self.clear_inputs() 

         #if self.use_current_time_checkbox.isChecked():
         #    timestamp_ms = self.current_timestamp_ms
         #else:
         #    raw = self.timestamp_input.text().strip()
         #    if not raw.isdigit():
         #        QMessageBox.warning(
         #            self,
         #            "Invalid Timestamp",
         #            "Timestamp must be an integer number of milliseconds.",
         #        )
         #        return
         #    timestamp_ms = int(raw)

         #entry = CommentEntry(
         #    timestamp_ms=timestamp_ms,
         #    data_point=data_point,
         #    comment=comment_text,
         #)
         #self.comments.append(entry)
         #self._add_list_item(entry)
         #self.comment_input.clear()
         #self.data_point_input.clear() 

    def _add_list_item(self, entry: CommentEntry):
        header = f"{format_ms(entry.start_time_ms)} - {format_ms(entry.end_time_ms)}"
        #if entry.data_point:
           # header += f" | {entry.data_point}"

        preview = entry.comment.replace("\n", " ")
        if len(preview) > 60:
            preview = preview[:57] + "..."

        item_text = f"{header}\n{preview}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, entry.start_time_ms)
        self.comment_list.addItem(item)

    def _jump_to_comment(self, item: QListWidgetItem):
        timestamp_ms = item.data(Qt.UserRole)
        if isinstance(timestamp_ms, int):
            self.jumpRequested.emit(timestamp_ms)

    def clear_inputs(self):
        self.start_time_input.clear()
        self.end_time_input.clear()
        self.side_input.clear()
        self.rass_input.clear()
        self.movement_input.clear()
        self.comment_input.clear()

    def get_comments(self) -> List[CommentEntry]:
        return self.comment_keeper.get_comments()