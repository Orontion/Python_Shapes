import sys
from random import randint
from math import ceil

from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPainter, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

import constants
from custom_shape import CustomShape

class CustomRect(CustomShape):
    def __init__(self, centerPoint: QPoint, size: QSize, color: QColor) -> None:
        self._size = size
        self._geometryObject = QRect(CustomRect.__calculateAnchorPoint(centerPoint, size), self._size)
        super().__init__(centerPoint, color, self._geometryObject)

    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def color(self) -> QColor:
        return self._color

    def __calculateAnchorPoint(centerPoint: QPoint, size: QSize) -> QPoint:
        min_x = ceil(centerPoint.x() - (size.width() - 1) / 2)
        min_y = ceil(centerPoint.y() - (size.height() -1) / 2)

        return QPoint(min_x, min_y)
    
    def setNewCenterPoint(self, point: QPoint) -> None:
        self._centerPoint = point
        self._geometryObject.moveCenter(self._centerPoint)

    def getLinkPoint(self, shape: CustomShape) -> QPoint:
        linkPoint = QPoint()

        borderDeltaX = 0
        borderDeltaY = 0

        if shape.centerPoint.x() > self.centerPoint.x():
            if shape.getBottomLeftBound().x() > self.getBottomRightBound().x():
                borderDeltaX = shape.getBottomLeftBound().x() - self.getBottomRightBound().x()
        else:
            if shape.getBottomRightBound().x() < self.getBottomLeftBound().x():
                borderDeltaX = shape.getBottomRightBound().x() - self.getBottomLeftBound().x()

        if shape.centerPoint.y() > self.centerPoint.y():
            if shape.getTopRightBound().y() > self.getBottomRightBound().y():
                borderDeltaY = shape.getTopRightBound().y() - self.getBottomRightBound().y()
        else:
            if shape.getBottomRightBound().y() < self.getTopRightBound().y():
                borderDeltaY = shape.getBottomRightBound().y() - self.getTopRightBound().y()

        if abs(borderDeltaX) > abs(borderDeltaY):
            linkPoint.setY(self._centerPoint.y())

            if borderDeltaX > 0:
                linkPoint.setX(self.getBottomRightBound().x())
            else:
                linkPoint.setX(self.getBottomLeftBound().x())
            
        else:
            linkPoint.setX(self._centerPoint.x())

            if borderDeltaY > 0:
                linkPoint.setY(self.getBottomRightBound().y())
            else:
                linkPoint.setY(self.getTopRightBound().y())

        return linkPoint

    def drawCustomShape(self, painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(self._geometryObject)

    def checkIntersection(self, shape: CustomShape) -> bool:
        return self._boundaryRect.intersects(shape.boundaryRect)

    def isPointOnShape(self, point: QPoint) -> bool:
        return self._geometryObject.contains(point)

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