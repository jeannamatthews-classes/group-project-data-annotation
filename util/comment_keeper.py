<<<<<<< HEAD
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
=======
from dataclasses import dataclass
from typing import List
import bisect
import datetime
import re
>>>>>>> origin/video_comments

from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QWidget
)

from PySide6.QtCore import QObject, Qt, Signal

from util.popups import save_popup_ui

def format_ms(ms: int) -> str:
    total_seconds = max(0, ms // 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{minutes:02}:{seconds:02}"

""" 
Accept string of form hh:mm:ss
Returns time in ms
    """
def to_ms(time:str) -> int:
    pattern = r"^(?:(\d+):)?(\d{2}):(\d{2})$"
    
    match = re.match(pattern, time)

    if match:
        hh, mm, ss = match.groups()
        
        # Default hours to '0' if not present
        hh = hh if hh is not None else "0"
        
        return ((hh*60 + mm) * 60 +ss) * 100
    
    raise ValueError(f"Invalid time format: '{time}'. Expected 'hh:mm:ss' or 'mm:ss'.")

@dataclass
class CommentEntry:
<<<<<<< HEAD
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
=======
    start_time_ms: int      = 0
    end_time_ms: int        = 0
    side: str               = ""
    RASS: str               = ""
    movement: str           = ""
    comment: str            = ""
    datetime_created: str   = ""

    def __lt__(self, other):
        return self.start_time_ms < other.start_time_ms

class CommentKeeper(QWidget):
>>>>>>> origin/video_comments
    """
    Keeps track of all project comments including, adding, removing, selecting, and displaying non-selected comments 
    """
    
    # Create Signal for changing selected comment
    selected_comment_changed = Signal(int)

    def __init__(self, list_widget: QListWidget):
        # Call QObject initPIP
        super().__init__()

        self.list_widget = list_widget

        # Create List for comments
        self.comments: List[CommentEntry] = []
<<<<<<< HEAD
        # Select Empty comment by default
        self.selected: Optional[CommentEntry] = None
=======

        # Select Empty comment by default
        self.select_empty_comment()      

    def select_empty_comment(self):
        emptyComment = CommentEntry()
        self.selected = emptyComment
        
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
            if self._save_popup_ui("Do you want to save your comment changes?"): self.save_comment(newComment)

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
        if not self.selected.datetime_created:
            self.selected.datetime_created = str(datetime.datetime.now())
        index = bisect.bisect_left(self.comments, newComment)
        self.comments.insert(index, newComment)
        self._insert_comment_to_widget(index, newComment)


    def save_comment(self, newComment: CommentEntry = None):
        if not self.selected.start_time_ms: 
            QMessageBox.warning(self, "Missing Start Time", "Please enter Start Time")
            return
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
        else: 
            self.comments[self.selected_index] = newComment
            self.list_widget.takeItem(self.selected_index)
            self._append_comment_to_widget(self.selected_index, newComment)

    def delete_current_comment(self):
        if self.selected_index == -1:
            raise ValueError
        self.comments.pop(self.selected_index)
        self.list_widget.takeItem(self.selected_index)

        self.select_empty_comment()

    def _format_comment(self, entry: CommentEntry):
        header = f"{format_ms(entry.start_time_ms)} - {format_ms(entry.end_time_ms)}"
        
        
        preview = entry.comment.replace("\n", " ")
        if len(preview) > 60:
            preview = preview[:57] + "..."

        item_text = f"{header}\n{preview}"
        item = QListWidgetItem(item_text)
        # item.setData(Qt.ItemDataRole.UserRole, entry.start_time_ms)
        return item

    def _insert_comment_to_widget(self, index: int, entry: CommentEntry):
        self.list_widget.insertItem(index, self._format_comment(entry))

    def _append_comment_to_widget(self, entry: CommentEntry):
        self.list_widget.addItem(self._format_comment(entry))

    def sync_list (self, current_time_ms):
        index = bisect.bisect_left(self.comments, current_time_ms, key=lambda x: x.start_time_ms)
        
        active_index = max(0, index - 1)
        
        if active_index < self.list_widget.count():
            item = self.list_widget.item(active_index)
            
            # Scroll so the active comment is at the top (or center)
            self.list_widget.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtTop)
            
            # Optionally highlight it
            self.list_widget.setCurrentItem(item)

    def update_start_time(self, time: str):
        try:  self.select_comment.start_time_ms = to_ms(time)
        except ValueError as e: QMessageBox.warning(self, f"{e}", "Please enter Valid Time")

    def update_end_time(self, time:str):
        try:  
            time_ms = to_ms(time)
            if self.start_time_ms > self.end_time_ms: 
                QMessageBox.warning(self, "Start Time must be less than End Time", "Please enter Valid Time")
            else: self.select_comment.end_time_ms = time_ms
        except ValueError as e: QMessageBox.warning(self, f"{e}", "Please enter Valid Time")
>>>>>>> origin/video_comments


<<<<<<< HEAD
    def add_comment(self, entry: CommentEntry) -> CommentEntry:
        self.comments.append(entry)
        self.comments.sort(key=lambda c: c.start_time_ms)
        return entry

    def delete_comment(self, entry: CommentEntry) -> None:
        if entry in self.comments:
            self.comments.remove(entry)
            if self.selected is entry:
                self.selected = None
=======

>>>>>>> origin/video_comments

    """ Ingests comments from JSON into object -- IMPLEMENT after JSON_Handler Merge """
    def import_comments(self):
        pass

<<<<<<< HEAD
    def get_comments(self) -> List[CommentEntry]:
        return list(self.comments)

    def comments_ui(self, layout):
         # Saved Comments
        layout.addWidget(QLabel("Saved comments:"))
        self.comment_list = QListWidget()
        layout.addWidget(self.comment_list, stretch=1)
=======
        self.list_widget.setUpdatesEnabled(False) # Prevents flickering
        self.list_widget.clear()
        
        for entry in self.comments:
            self._append_comment_to_widget(entry)
            
        self.list_widget.setUpdatesEnabled(True)

    def save_comments(self):
        pass

if __name__ == "__main__":
    pass
>>>>>>> origin/video_comments
