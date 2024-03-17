from PyQt5.QtWidgets import QToolBar

import constants

class MainToolbar(QToolBar):
    def __init__(self) -> None:
        super().__init__()
        self.addRectBtn = self.addAction(constants.ADD_RECT_BUTTON)
        self.addLinkBtn = self.addAction(constants.ADD_LINK_BUTTON)

        self.addSeparator()

        self.moveRectButton = self.addAction(constants.MOVE_RECT_BUTTON)

        self.addSeparator()

        self.clearBtn = self.addAction(constants.CLEAR_DRAW_AREA_BUTTON)