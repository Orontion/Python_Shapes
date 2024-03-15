import sys

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPainter

import constants
import main_toolbar
import draw_area

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(constants.MAIN_WINDOW_START_POSITION_X,
                         constants.MAIN_WINDOW_START_POSITION_Y, 
                         constants.MAIN_WINDOW_SIZE_X,
                         constants.MAIN_WINDOW_SIZE_Y)
        
        self._createToolBar()

        self.draw_area = draw_area.DrawArea(self)

        self.setCentralWidget(self.draw_area)

        self.show()

        # self.draw_area.refreshSize()

    def _createToolBar(self):
        tools = main_toolbar.MainToolbar()
        self.addToolBar(tools)

    # def paintEvent(self, event):
    #     width = self.pos2[0]-self.pos1[0]
    #     height = self.pos2[1] - self.pos1[1]     

    #     qp = QPainter()
    #     qp.begin(self)           
    #     qp.drawRect(self.pos1[0], self.pos1[1], width, height)        
    #     qp.end()

    # def mousePressEvent(self, event):
    #     self.pos1[0], self.pos1[1] = event.pos().x(), event.pos().y()
    #     print("clicked")

    # def mouseReleaseEvent(self, event):
    #     self.pos2[0], self.pos2[1] = event.pos().x(), event.pos().y()
    #     print("released")
    #     self.update()