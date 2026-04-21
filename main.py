import os
os.environ["QT_LOGGING_RULES"] = "qt.multimedia.*=false"

import sys
from PySide6.QtWidgets import QApplication
from main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("Data Anotation")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()