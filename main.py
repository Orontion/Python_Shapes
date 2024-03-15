import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget

import constants
import main_window

app = QApplication([])

window = main_window.MainWindow()

sys.exit(app.exec())