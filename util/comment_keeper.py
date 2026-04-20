from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import bisect
import re



from PySide6.QtCore import QObject, Qt, Signal, QSignalBlocker
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView

from util.popups import save_popup_ui

def format_ms(ms: int) -> str:
    total_seconds = max(0, int(ms) // 1000)
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
def to_ms(time_str: str) -> int:
    """
    Accepts:
      - mm:ss
      - hh:mm:ss
      - raw integer milliseconds
    Returns milliseconds as int.
    """
    raw = time_str.strip()
    if not raw:
        raise ValueError("Time cannot be empty.")

    if raw.isdigit():
        return int(raw)

    pattern = r"^(?:(\d+):)?(\d{1,2}):(\d{2})$"
    match = re.match(pattern, raw)
    if not match:
        raise ValueError(
            f"Invalid time format: '{time_str}'. Expected mm:ss, hh:mm:ss, or milliseconds."
        )

    hh, mm, ss = match.groups()
    hours = int(hh) if hh is not None else 0
    minutes = int(mm)
    seconds = int(ss)

    return ((hours * 60 + minutes) * 60 + seconds) * 1000


@dataclass(order=True)
class CommentEntry:
    start_time_ms: int = 0
    end_time_ms: int = 0
    side: str = ""
    RASS: str = ""
    movement: str = ""
    comment: str = ""
    datetime_created: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )

class CommentKeeper(QObject):
    """
    Owns the comment list, the selected comment index,
    and the comment currently being edited.
    """

    selected_comment_changed = Signal(int)

    def __init__(self, list_widget: QListWidget):
        super().__init__()
        self.list_widget = list_widget
        self.comments: List[CommentEntry] = []
        self.selected_index: int = -1
        self.selected: CommentEntry = CommentEntry()
        self._last_synced_index: Optional[int] = None

    def get_comments(self) -> List[CommentEntry]:
        return list(self.comments)

    def select_empty_comment(self) -> None:
        self.selected_index = -1
        self.selected = CommentEntry()
        self.selected_comment_changed.emit(-1)

    def select_comment(self, index: int) -> None:
        if index < 0 or index >= len(self.comments):
            self.select_empty_comment()
            return

        self.selected_index = index
        entry = self.comments[index]
        self.selected = CommentEntry(
            start_time_ms=entry.start_time_ms,
            end_time_ms=entry.end_time_ms,
            side=entry.side,
            RASS=entry.RASS,
            movement=entry.movement,
            comment=entry.comment,
            datetime_created=entry.datetime_created,
        )
        self.selected_comment_changed.emit(index)

    def save_comment(self, new_comment: Optional[CommentEntry] = None) -> int:
        if new_comment is not None:
            self.selected = new_comment

        if self.selected.end_time_ms < self.selected.start_time_ms:
            self.selected.start_time_ms, self.selected.end_time_ms = (
                self.selected.end_time_ms,
                self.selected.start_time_ms,
            )

        if not self.selected.datetime_created:
            self.selected.datetime_created = datetime.now().isoformat(timespec="seconds")

        if self.selected_index == -1:
            self.comments.append(self.selected)
        else:
            self.comments[self.selected_index] = self.selected

        self.comments.sort(key=lambda c: c.start_time_ms)

        # Find the saved comment's new index after sorting.
        self.selected_index = self._find_comment_index(self.selected)
        self.refresh_list()

        with QSignalBlocker(self.list_widget):
            if 0 <= self.selected_index < self.list_widget.count():
                self.list_widget.setCurrentRow(self.selected_index)

        self.selected_comment_changed.emit(self.selected_index)
        return self.selected_index


    def delete_current_comment(self) -> None:
        if self.selected_index < 0 or self.selected_index >= len(self.comments):
            return

        del self.comments[self.selected_index]
        self.refresh_list()
        self.select_empty_comment()

    def maybe_save_current(self, candidate: CommentEntry) -> bool:
        """
        Optional helper if you want a save/discard prompt before switching comments.
        Returns True if it is okay to continue.
        """
        if self.selected_index == -1 and not self._has_meaningful_content(candidate):
            return True

        if candidate == self.selected:
            return True

        should_save = save_popup_ui("Do you want to save your comment changes?")
        if should_save:
            self.save_comment(candidate)
        return True

    def refresh_list(self) -> None:
        self.list_widget.setUpdatesEnabled(False)
        try:
            with QSignalBlocker(self.list_widget):
                self.list_widget.clear()
                for entry in self.comments:
                    self.list_widget.addItem(self._format_comment_item(entry))
        finally:
            self.list_widget.setUpdatesEnabled(True)

    def sync_list(self, current_time_ms: int) -> None:
        """
        Scrolls the list toward the currently active comment without changing
        the user's selected edit target.
        """
        if not self.comments or self.list_widget.count() == 0:
            return

        active_index = self._find_active_index(current_time_ms)
        if active_index is None or active_index == self._last_synced_index:
            return

        self._last_synced_index = active_index
        item = self.list_widget.item(active_index)
        if item is not None:
            self.list_widget.scrollToItem(
                item, QAbstractItemView.ScrollHint.PositionAtTop
            )

    def _find_active_index(self, current_time_ms: int) -> Optional[int]:
        # Prefer a comment whose full span contains the current time.
        for i, entry in enumerate(self.comments):
            if entry.start_time_ms <= current_time_ms <= entry.end_time_ms:
                return i

        # Otherwise use the latest comment that starts before the current time.
        starts = [entry.start_time_ms for entry in self.comments]
        idx = bisect.bisect_right(starts, current_time_ms) - 1
        if idx >= 0:
            return idx
        return None

    def _find_comment_index(self, target: CommentEntry) -> int:
        for i, entry in enumerate(self.comments):
            if (
                entry.start_time_ms == target.start_time_ms
                and entry.end_time_ms == target.end_time_ms
                and entry.side == target.side
                and entry.RASS == target.RASS
                and entry.movement == target.movement
                and entry.comment == target.comment
                and entry.datetime_created == target.datetime_created
            ):
                return i
        return -1

    def _has_meaningful_content(self, entry: CommentEntry) -> bool:
        return any(
            [
                entry.start_time_ms != 0,
                entry.end_time_ms != 0,
                bool(entry.side.strip()),
                bool(entry.RASS.strip()),
                bool(entry.movement.strip()),
                bool(entry.comment.strip()),
            ]
        )

    def _format_comment_item(self, entry: CommentEntry) -> QListWidgetItem:
        header = f"{format_ms(entry.start_time_ms)} - {format_ms(entry.end_time_ms)}"

        preview = entry.comment.replace("\n", " ")
        if len(preview) > 60:
            preview = preview[:57] + "..."

        item_text = f"{header}\n{preview}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, entry.start_time_ms)
        return item

    def import_comments(self):
        pass

    def save_comments(self):
        pass