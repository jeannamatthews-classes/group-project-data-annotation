from dataclasses import dataclass
from typing import List
import bisect
import datetime

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
        self.select_empty_comment()

        # Keeps track of the current selected index (-1 means new comment)
        self.selected_index = -1

       

    def select_empty_comment(self):
        emptyComment = CommentEntry
        self.selected = emptyComment

        self.start_time_ms = 0
        self.end_time_ms = 0
        self.side = ""
        self.RASS = 0
        self.movement = ""
        self.comment = ""
        self.datetime_created = ""

    def select_comment(self, index: int):
        self.select_comment = self.comments[index]
        self.selected_index = index

        self.start_time_ms = self.select_comment.start_time_ms
        self.end_time_ms = self.select_comment.end_time_ms
        self.side = self.select_comment.side
        self.RASS = self.select_comment.RASS
        self.movement = self.select_comment.movement
        self.comment = self.select_comment.comment
        self.datetime_created = self.select_comment.datetime_created

    def add_comment(self):
        if not self.datetime_created:
            self.select_comment.datetime_created = str(datetime.datetime.now())
        bisect.insort(self.comments, self.select_comment, key=lambda x: x.start_time_ms)
        self.select_empty_comment()

    def delete_current_comment(self):
        if self.selected_index == -1:
            raise ValueError
        self.comments.pop(self.selected_index)

    """ Ingests comments from JSON into object -- IMPLEMENT after JSON_Handler Merge """
    def import_comments():
        pass

    def comments_ui(self, layout):
         # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)