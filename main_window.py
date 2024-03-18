from PyQt5.QtWidgets import QMainWindow

import constants
from main_toolbar import MainToolbar
from draw_area import DrawArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(constants.MAIN_WINDOW_START_POSITION_X,
                         constants.MAIN_WINDOW_START_POSITION_Y, 
                         constants.MAIN_WINDOW_SIZE_X,
                         constants.MAIN_WINDOW_SIZE_Y)
        
        # Prohibit resizing
        self.setFixedSize(self.width(), self.height())
        
        # Drawing widget
        self.draw_area = DrawArea(self)
        self.setCentralWidget(self.draw_area)

        # Toolbar to control drawing widget
        self._createToolBar(self.draw_area)
        
        self.show()

    def _createToolBar(self, draw_area: DrawArea):
        tools = MainToolbar()
        self.addToolBar(tools)
        
        tools.addRectBtn.triggered.connect(draw_area.startRectCreation)
        tools.addLinkBtn.triggered.connect(draw_area.startLinkCreation)
        tools.moveShapeButton.triggered.connect(draw_area.startRectMove)
        tools.clearBtn.triggered.connect(draw_area.clearArea)
        