import sys

from typing import Union, List

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
# from custom_rect import CustomRect
from custom_shape import CustomShape

class ShapesCollection():
    def __init__(self) -> None:
        self._nodesList: List[CustomShape] = []

    @property
    def nodesList(self) -> List[CustomShape]:
        return self._nodesList

    def addShape(self, shape: CustomShape, dimensionStart: int = 0) -> None:
        self._nodesList.append(shape)

    def getShapeAtPoint(self, point: QPoint) -> CustomShape:
        for node in self._nodesList:
            if node.isPointOnShape(point):
                return node

        return None
    
    def deleteShape(self, shape: CustomShape) -> None:
        self._nodesList.remove(shape)

class CollisionProcessor():
    def __init__(self, drawingWidget: QWidget, shapesCollection: ShapesCollection) -> None:
        self._drawingWidget = drawingWidget
        self._shapesCollection = shapesCollection

    # Check if new shape fits into draw area
    def areaBorderCheck(self, shape: CustomShape) -> bool:
        if shape.getTopLeftBound().x() < 0 or shape.getTopLeftBound().y() < 0:
            return False

        if shape.getBottomRightBound().x() > self._drawingWidget.width() or shape.getBottomRightBound().y() > self._drawingWidget.height():
            return False
        
        return True
    
    #Check collisions with other shapes
    def shapeCollisionCheck(self, shape: CustomShape) -> bool:
        for node in self._shapesCollection.nodesList:
            if node and shape.checkIntersection(node):
                return False
            
        return True
    
    # Complete collision check
    def completeCollisionCheck(self, shape: CustomShape) -> bool:
        return self.areaBorderCheck(shape) and self.shapeCollisionCheck(shape)