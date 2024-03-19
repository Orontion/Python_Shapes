from typing import List

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint

from custom_shape import CustomShape

# Class with custom shapes collection
# Main goals: store all shapes on a plane, add/modify/delete shapes,
# effectively search for a shape at certain point
# effectively search for nearest shape(s) to point/to shape
#
# Implemetation below is ineffective and does not implement nearest shape(s) search
class ShapesCollection():
    def __init__(self) -> None:
        self._nodesList: List[CustomShape] = []

    @property
    def nodesList(self) -> List[CustomShape]:
        return self._nodesList

    def addShape(self, shape: CustomShape) -> None:
        self._nodesList.append(shape)

    def getShapeAtPoint(self, point: QPoint) -> CustomShape:
        for node in self._nodesList:
            if node.isPointOnShape(point):
                return node

        return None
    
    def deleteShape(self, shape: CustomShape) -> None:
        self._nodesList.remove(shape)

    def clearCollection(self) -> None:
        self._nodesList.clear()

# Class to check for shapes collisions/overlaps
# Requires area to process borders collisions 
# and collection of shapes to process collisions between shapes
#
# Current implemetation is ineffective and uses simple iterating through entire shapes collection
# This works for a small number of shapes, but will lead to poor performance for bigger collection
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
    
    # Check collisions with other shapes
    def shapeCollisionCheck(self, shape: CustomShape) -> bool:
        for node in self._shapesCollection.nodesList:
            if node != shape and shape.checkIntersection(node):
                return False
            
        return True
    
    # Complete collision check
    def completeCollisionCheck(self, shape: CustomShape) -> bool:
        return self.areaBorderCheck(shape) and self.shapeCollisionCheck(shape)