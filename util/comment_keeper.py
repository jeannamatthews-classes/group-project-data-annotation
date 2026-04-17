from dataclasses import dataclass
from typing import List
import bisect
import datetime

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QVBoxLayout,
    QMessageBox,
)

from PySide6.QtCore import QObject, Signal

@dataclass
class CommentEntry:
    start_time_ms: int
    end_time_ms: int
    side: str
    RASS: str
    movement: str
    comment: str
    datetime_created: str

class CommentKeeper(QObject):
    """
    Keeps track of all project comments including, adding, removing, selecting, and displaying non-selected comments 
    """
    
    # Create Signal for changing selected comment
    selected_comment_changed = Signal(int)

    def __init__(self):
        # Call QObject init
        super().__init__()

        # Create List for comments
        self.comments: List[CommentEntry] = []

        # Select Empty comment by default
        self.select_empty_comment()      

    def select_empty_comment(self):
        emptyComment = CommentEntry
        self.selected = emptyComment

        self.start_time_ms = 0
        self.end_time_ms = 0
        self.side = ""
        self.RASS = ""
        self.movement = ""
        self.comment = ""
        self.datetime_created = ""
        
        # Keeps track of the current selected index (-1 means new comment)
        self.selected_index = -1

        self.selected_comment_changed.emit(-1)

    def select_comment(self, index: int):
        if self.selected_index == index:
            return  # do nothing if not switching comment

        # Check that comment is Modified
        newComment = CommentEntry(
            self.select_comment.start_time_ms,
            self.select_comment.end_time_ms,
            self.select_comment.side,
            self.select_comment.RASS,
            self.select_comment.movement,
            self.select_comment.comment,
            self.select_comment.datetime_created
        )
        self.selected_comment_changed.emit(self.selected_index)

        if not newComment == self.selected:
            # Unsaved Changes Exist - Ask to save
            if self._save_popup_ui(): self.save_comment(newComment)

        # Switch Comments
        self.select_comment = self.comments[index]
        self.selected_index = index

        self.start_time_ms = self.select_comment.start_time_ms
        self.end_time_ms = self.select_comment.end_time_ms
        self.side = self.select_comment.side
        self.RASS = self.select_comment.RASS
        self.movement = self.select_comment.movement
        self.comment = self.select_comment.comment
        self.datetime_created = self.select_comment.datetime_created

        self.selected_comment_changed.emmit()

    def add_comment(self, newComment: CommentEntry):
        if not self.datetime_created:
            self.selected.datetime_created = str(datetime.datetime.now())
        bisect.insort(self.comments, self.select_comment, key=lambda x: x.start_time_ms)

    def save_comment(self, newComment: CommentEntry = None):
        if not newComment:
            newComment = CommentEntry(
            self.selected.start_time_ms,
            self.selected.end_time_ms,
            self.selected.side,
            self.selected.RASS,
            self.selected.movement,
            self.selected.comment,
            self.selected.datetime_created
            )
        if self.selected_index == -1: self.add_comment(newComment)
        else: self.comments[self.selected_index] = newComment

        self.select_empty_comment()

    def delete_current_comment(self):
        if self.selected_index == -1:
            raise ValueError
        self.comments.pop(self.selected_index)

        self.select_empty_comment()

    """ Ingests comments from JSON into object -- IMPLEMENT after JSON_Handler Merge """
    def import_comments():
        pass

    def _save_popup_ui() -> bool:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Save Prompt")
        msg_box.setText("Do you want to save your Comment Changes?")

        save_btn = msg_box.addButton("Save", QMessageBox.ActionRole)
        discard_btn = msg_box.addButton("Don't Save", QMessageBox.DestructiveRole)

        msg_box.exec()

        if msg_box.clickedButton() == save_btn:
            return True
        elif msg_box.clickedButton() == discard_btn:
            return False

    def comments_ui(self, layout: QVBoxLayout):
         # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)