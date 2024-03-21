from abc import ABC, abstractmethod

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QPoint, QRect

# Base class for all shapes being drawn
# Should have:
# - Center point as it's defining point
# - Boundary rect will be used to calculate collisions for different shapes
class CustomShape(ABC):
    @abstractmethod
    def __init__(self, centerPoint: QPoint, boundingBox: QRect) -> None:
        super().__init__()
        self._centerPoint = centerPoint
        self._boundingBox = boundingBox
        
    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def boundingBox(self) -> QRect:
        return self._boundingBox
    
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
        return self._boundingBox.topLeft()

    def getTopRightBound(self) -> QPoint:
        return self._boundingBox.topRight()
    
    def getBottomLeftBound(self) -> QPoint:
        return self._boundingBox.bottomLeft()

    def getBottomRightBound(self) -> QPoint:
        return self._boundingBox.bottomRight()

    # This method checks intersection with boundary of specified CustomShape
    @abstractmethod
    def checkIntersectionBoundary(self, shape: "CustomShape") -> bool:
        pass

    # This method checks intersection between actual shapes borders with specified CustomShape
    @abstractmethod
    def checkIntersectionPrecise(self, shape: "CustomShape") -> bool:
        pass

    # This method checks if specific point is located on the shape
    @abstractmethod
    def isPointOnShape(self, point: QPoint) -> bool:
        pass

# Base class for CustomShapes factories
class CustomShapeBaseFactory(ABC):
    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    # General factory method to produce custom shapes
    @abstractmethod
    def getNewCustomShape(self, centerPoint: QPoint) -> CustomShape:
        pass