import sys
from random import randint

from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPainter, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

import constants

class CustomRect(QRect):
    def __init__(self, centerPoint: QPoint, size: QSize, color: QColor) -> None:
        self._centerPoint = centerPoint
        self._size = size
        self._color = color

        super().__init__(CustomRect.calculateAnchorPoint(centerPoint, size), self._size)

    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def color(self) -> QColor:
        return self._color

    def calculateAnchorPoint(centerPoint: QPoint, size: QSize) -> QPoint:
        min_x = centerPoint.x() - size.width() // 2

        min_y = centerPoint.y() - size.height() // 2

        # Check for negative numbers?

        return QPoint(min_x, min_y)
    
    def setNewCenterPoint(self, dx: int, dy: int) -> None:
        self._centerPoint.setX(self._centerPoint.x() + dx)
        self._centerPoint.setY(self._centerPoint.y() + dy)
        self.moveCenter(self._centerPoint)

class CustomRectBaseFactory():
    def __init__(self) -> None:
        self._defaultSize: QSize = QSize(constants.RECT_SIZE_X, constants.RECT_SIZE_Y)
        self.__defaultColor: QColor = Qt.GlobalColor.black
    
    def getNewCustomRect(self, centerPoint: QPoint, size: QSize, color: QColor) -> CustomRect:
        return CustomRect(centerPoint, size, color)
    
    def getNewCustomRect(self, centerPoint: QPoint) -> CustomRect:
        return CustomRect(centerPoint, self._defaultSize, self.__defaultColor)
    
class CustomRectRandomColorFactory(CustomRectBaseFactory):
    def __init__(self) -> None:
        self.__colorTable = (Qt.GlobalColor.red,
                             Qt.GlobalColor.green,
                             Qt.GlobalColor.blue,
                             Qt.GlobalColor.yellow)
        super().__init__()

    def getNewCustomRect(self, centerPoint: QPoint) -> CustomRect:
        color = self.__colorTable[randint(0, len(self.__colorTable) - 1)]
        return CustomRect(centerPoint, self._defaultSize, color)