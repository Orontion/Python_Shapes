import sys

from typing import Union
from abc import ABC, abstractmethod, abstractproperty

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPainter, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

class CustomShape(ABC):
    @abstractmethod
    def __init__(self, centerPoint: QPoint, color: QColor, boundaryRect: QRect) -> None:
        super().__init__()
        self._centerPoint = centerPoint
        self._color = color
        self._boundaryRect = boundaryRect
        
    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def color(self) -> QColor:
        return self._color
    
    @property
    def boundaryRect(self) -> QRect:
        return self._boundaryRect
    
    @abstractmethod
    def setNewCenterPoint(self, dx: int, dy: int) -> None:
        pass

    @abstractmethod
    def getLinkPoint(self, shape: "CustomShape") -> QPoint:
        pass

    @abstractmethod
    def drawCustomShape(self, painter: QPainter) -> None:
        pass

    # These methods return points defining boundary rect of shape
    def getTopLeftBound(self) -> QPoint:
        return self._boundaryRect.topLeft()

    def getTopRightBound(self) -> QPoint:
        return self._boundaryRect.topRight()
    
    def getBottomLeftBound(self) -> QPoint:
        return self._boundaryRect.bottomLeft()

    def getBottomRightBound(self) -> QPoint:
        return self._boundaryRect.bottomRight()

    # This method checks intersection with specified CustomShape
    @abstractmethod
    def checkIntersection(self, shape: "CustomShape") -> bool:
        pass

    @abstractmethod
    def isPointOnShape(self, point: QPoint) -> bool:
        pass