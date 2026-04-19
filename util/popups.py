from PySide6.QtWidgets import QMessageBox

def save_popup_ui(popup_text: str) -> bool:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Save Prompt")
        msg_box.setText(popup_text)

        save_btn = msg_box.addButton("Save", QMessageBox.ActionRole)
        discard_btn = msg_box.addButton("Don't Save", QMessageBox.DestructiveRole)

        msg_box.exec()

        if msg_box.clickedButton() == save_btn:
            return True
        elif msg_box.clickedButton() == discard_btn:
            return False