import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAction, QMainWindow

import constants
import main_toolbar
from draw_area import DrawArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(constants.MAIN_WINDOW_START_POSITION_X,
                         constants.MAIN_WINDOW_START_POSITION_Y, 
                         constants.MAIN_WINDOW_SIZE_X,
                         constants.MAIN_WINDOW_SIZE_Y)
        
        self.draw_area = DrawArea(self)

        self._createToolBar(self.draw_area)

        self.setCentralWidget(self.draw_area)
        self.show()

    def _createToolBar(self, draw_area: DrawArea):
        tools = main_toolbar.MainToolbar()
        self.addToolBar(tools)
        
        tools.addRectBtn.triggered.connect(draw_area.startRectCreation)
        tools.addLinkBtn.triggered.connect(draw_area.startLinkCreation)
        tools.clearBtn.triggered.connect(draw_area.clearArea)