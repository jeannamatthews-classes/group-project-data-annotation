from dataclasses import dataclass, replace
from typing import List
import bisect
import datetime
import re

from PySide6.QtWidgets import (
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QWidget,
    QFileDialog
)

from PySide6.QtCore import QObject, Qt, Signal
from util.popups import save_popup_ui
import util.json_handler as json

def format_ms(ms: int) -> str:
    if ms is None: return ""
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
        
        return ((int(hh)*60 + int(mm)) * 60 + int(ss)) * 1000
    
    raise ValueError(f"Invalid time format: '{time}'. Expected 'hh:mm:ss' or 'mm:ss'.")

@dataclass
class CommentEntry:
    start_time_ms: int      = None
    end_time_ms: int        = None
    side: str               = ""
    RASS: str               = ""
    movement: str           = ""
    comment: str            = ""
    datetime_created: str   = None

    def __lt__(self, other):
        return self.start_time_ms < other.start_time_ms

def _format_comment(comment: CommentEntry):
    header = f"{format_ms(comment.start_time_ms)} - {format_ms(comment.end_time_ms)}"

    preview = comment.comment.replace("\n", " ")
    if len(preview) > 45:
        preview = preview[:42] + "..."

    item_text = f"{header}\n{preview}"
    item = QListWidgetItem(item_text)
    item.setData(Qt.ItemDataRole.UserRole, comment.start_time_ms)
    return item

class CommentKeeper(QWidget):
    """
    Keeps track of all project comments including, adding, removing, selecting, and displaying non-selected comments 
    """
    
    # Create Signal for changing selected comment
    selected_comment_changed = Signal(int)

    def __init__(self, list_widget: QListWidget):
        # Call QObject initPIP
        super().__init__()

        self.list_widget = list_widget
        self.list_widget.currentRowChanged.connect(self.select_comment)

        # Create List for comments
        self.comments: List[CommentEntry] = []

        # Select Empty comment by default
        self.select_empty_comment()      

    def select_empty_comment(self):
        self.selected = CommentEntry()
        self.working = replace(self.selected)
        
        # Keeps track of the current selected index (-1 means new comment)
        self.selected_index = -1
        self.list_widget.clearSelection()

    def select_comment(self, index: int):
        if self.selected_index == index:
            return  # do nothing if not switching comment

        if not self.working == self.selected:
            # Unsaved Changes Exist - Ask to save
            if self._save_popup_ui("Do you want to save your comment changes?"): self.save_comment(self.working)

        # Switch Comments
        if index == -1: self.select_empty_comment()
        else:
            self.selected = self.comments[index]
            self.selected_index = index
            self.working = replace(self.selected)
            self.list_widget.setCurrentRow(index)

        self.selected_comment_changed.emit(self.selected_index)

    def get_comments(self):
        return list(self.comments)

    def add_comment(self):
        self.working.datetime_created = str(datetime.datetime.now())
        index = bisect.bisect_left(self.comments, self.working)
        self.comments.insert(index, self.working)
        self.selected = self.comments[index]
        self._insert_comment_to_widget(index)
        self.selected_index = index
        self.selected_comment_changed.emit(self.selected_index)
        

    def save_comment(self):
        if self.working.start_time_ms is None: 
            QMessageBox.warning(self, "Missing Start Time", "Please enter Start Time")
            return

        if self.selected_index == -1: self.add_comment()
        elif not self.working == self.selected: 
            self.comments[self.selected_index] = self.working
            self.list_widget.takeItem(self.selected_index)
            self._insert_comment_to_widget(self.selected_index)

    def delete_current_comment(self):
        if self.selected_index == -1:
            raise ValueError
        self.comments.pop(self.selected_index)
        self.list_widget.takeItem(self.selected_index)

        self.select_empty_comment()

    
    def _insert_comment_to_widget(self, index: int):
        self.list_widget.insertItem(index, _format_comment(self.working))

    def _append_comment_to_widget(self, comment):
        header = f"{format_ms(comment.start_time_ms)} - {format_ms(comment.end_time_ms)}"
        preview = comment.comment.replace("\n", " ")
        item_text = f"{header}\n{preview}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, comment.start_time_ms)
        self.list_widget.addItem(item)

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

    """ Ingests comments from JSON into object """
    def import_json_comments(self, path):
        self.json_path = path

        self.comments = json.read_list(CommentEntry, path)
        self.list_widget.setUpdatesEnabled(False)
        self.list_widget.clear()
        
        for entry in self.comments:
            self._append_comment_to_widget(entry)
            
        self.list_widget.setUpdatesEnabled(True)

    def save_json_comments(self):

        if not self.json_path and not self.comments: 
            self.json_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save JSON File",
                "",
                "JSON Files (*json);;All Files (*)"
            )

        json.write(self.comments, self.json_path)


if __name__ == "__main__":
    pass