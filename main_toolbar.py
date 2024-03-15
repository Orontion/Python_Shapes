import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

import constants

class MainToolbar(QtWidgets.QToolBar):
    def __init__(self) -> None:
        super().__init__()
        self.addAction(constants.ADD_RECT_BUTTON)

        self.addAction(constants.ADD_LINK_BUTTON)

        self.addSeparator()

        self.addAction(constants.CLEAR_DRAW_AREA_BUTTON)