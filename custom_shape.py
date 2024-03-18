from abc import ABC, abstractmethod

from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import QPoint, QRect

# Base class for all shapes being drawn
# Should have:
# - Center point as it's defining point
# - Boundary rect will be used to calculate collisions for different shapes
class CustomShape(ABC):
    @abstractmethod
    def __init__(self, centerPoint: QPoint, boundaryRect: QRect) -> None:
        super().__init__()
        self._centerPoint = centerPoint
        self._boundaryRect = boundaryRect
        
    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def boundaryRect(self) -> QRect:
        return self._boundaryRect
    
    @abstractmethod
    def setNewCenterPoint(self, point: QPoint) -> None:
        pass

    # Returns optimal point on shape to position link to specified shape
    @abstractmethod
    def getLinkPoint(self, shape: "CustomShape") -> QPoint:
        pass

    # Draws the shape using specified QPainter
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

    # This method checks if specific point is located on the shape
    @abstractmethod
    def isPointOnShape(self, point: QPoint) -> bool:
        pass