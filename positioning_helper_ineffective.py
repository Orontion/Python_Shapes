import sys

from typing import Union, List

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
from custom_rect import CustomRect

class ShapesCollection():
    def __init__(self) -> None:
        self._nodesList: List[CustomRect] = []

    @property
    def nodesList(self) -> List[CustomRect]:
        return self._nodesList

    def addShape(self, shape: CustomRect, dimensionStart: int = 0) -> None:
        self._nodesList.append(shape)

    def getShapeAtPoint(self, point: QPoint) -> CustomRect:
        for node in self._nodesList:
            if node.contains(point):
                return node

        return None
    
    def deleteShape(self, shape: CustomRect) -> None:
        self._nodesList.remove(shape)

class CollisionProcessor():
    def __init__(self, drawingWidget: QWidget, shapesCollection: ShapesCollection) -> None:
        self._drawingWidget = drawingWidget
        self._shapesCollection = shapesCollection

    # Check if new shape fits into draw area
    def areaBorderCheck(self, shape: CustomRect) -> bool:
        print("area check")
        if shape.top() < 0 or shape.left() < 0:
            print("Failed top or left")
            return False

        if shape.bottom() > self._drawingWidget.height() or shape.right() > self._drawingWidget.width():
            print("Failed bottom or right")
            return False
        
        return True
    
    #Check collisions with other shapes
    def shapeCollisionCheck(self, shape: CustomRect) -> bool:
        for node in self._shapesCollection.nodesList:
            if node and shape.intersects(node):
                return False
            
        return True
    
    # Complete collision check
    def completeCollisionCheck(self, shape: CustomRect) -> bool:
        return self.areaBorderCheck(shape) and self.shapeCollisionCheck(shape)
    
    # Check collisions before actual move
    def checkMovePossibility(self, shape: CustomRect, delta_x: int, delta_y: int) -> bool:
        new_center = QPoint(shape.centerPoint.x() + delta_x, shape.centerPoint.y() + delta_y)

        # TODO: Dummy shape should be twin class for without any functions except for size
        # used only to do collision check
        dummy_shape = CustomRect(new_center, shape.size(), shape.color)

        return self.completeCollisionCheck(dummy_shape)