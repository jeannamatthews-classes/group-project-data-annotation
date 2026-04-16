from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
)

@dataclass
class CommentEntry:
    start_time_ms: int
    end_time_ms: int
    side: str = ""
    RASS: int = 0
    movement: str = ""
    comment: str = ""
    datetime_created: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )
class CommentKeeper:
    """
    Keeps track of all project comments including, adding, removing, selecting, and displaying non-selected comments 
    """

    def __init__(self):
        # Create List for comments
        self.comments: List[CommentEntry] = []
        # Select Empty comment by default
        self.selected: Optional[CommentEntry] = None

    def select_comment():
        pass

    def add_comment(self, entry: CommentEntry) -> CommentEntry:
        self.comments.append(entry)
        self.comments.sort(key=lambda c: c.start_time_ms)
        return entry

    def delete_comment(self, entry: CommentEntry) -> None:
        if entry in self.comments:
            self.comments.remove(entry)
            if self.selected is entry:
                self.selected = None

    """ Ingests comments from JSON into object -- IMPLEMENT after JSON_Handler Merge """
    def import_comments():
        pass

    def get_comments(self) -> List[CommentEntry]:
        return list(self.comments)

    def comments_ui(self, layout):
         # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)