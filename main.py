import sys

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication([])

window = MainWindow()

sys.exit(app.exec())