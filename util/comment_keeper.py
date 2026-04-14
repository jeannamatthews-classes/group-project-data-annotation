from dataclasses import dataclass
from typing import List

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
)

@dataclass
class CommentEntry:
    start_time_ms: int
    end_time_ms: int
    side: str
    RASS: int
    movement: str
    comment: str
    datetime_created: str

class CommentKeeper:
    """
    Keeps track of all project comments including, adding, removing, selecting, and displaying non-selected comments 
    """

    def __init__(self):
        # Create List for comments
        self.comments: List[CommentEntry] = []


        # Select Empty comment by default
        emptyComment = CommentEntry
        self.selected = emptyComment

    def select_comment():
        pass

    def add_comment():
        pass

    def delete_comment():
        pass

    """ Ingests comments from JSON into object -- IMPLEMENT after JSON_Handler Merge """
    def import_comments():
        pass

    def comments_ui(self, layout):
         # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)