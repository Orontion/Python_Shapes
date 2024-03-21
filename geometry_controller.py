from typing import List

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QPoint

from custom_rect import CustomRect
from custom_shape import CustomShape, CustomShapeBaseFactory
# TODO: Test which positioning helper is actually more effective
from positioning_helper_v2 import ShapesCollection, CollisionProcessor
# from positioning_helper_ineffective import ShapesCollection, CollisionProcessor
from shapes_link import ShapesLinkBase, ShapesLinkLine

class GeometryController():
    def __init__(self, drawArea: QWidget) -> None:
        # Collections for shapes and links
        self._shapesCollection = ShapesCollection()
        self._shapeLinksCollection: List[ShapesLinkBase] = []           # TODO: Should restrict duplicate link creation (WHAT IS a duplicate link?)

        # Checker for collisions
        # TODO: Find better solution, had to pass drawArea as QWidget due to dynamic size
        self._collisionChecker = CollisionProcessor(drawArea, self._shapesCollection)

        # Selected shape is being excluded from _shapesCollection to optimize shape update during movement
        self._selectedShape: CustomRect = None

    @property
    def selectedShape(self) -> CustomShape:
        return self._selectedShape

    # Try to select shape at certain point, returns true if success
    # Selected shape is removed from shapes collection for proper position tracking
    def trySelectShape(self, point: QPoint) -> bool:
        if self._selectedShape:
            if self._selectedShape.isPointOnShape(point):
                return True
            else:
                self.__deselectShape()

        self._selectedShape = self._shapesCollection.popShapeAtPoint(point)
        if self._selectedShape:
            return True
        else:
            return False

    # Clear selected shape
    def clearSelectedShape(self) -> None:
        self.__deselectShape()

    # Checks if there is a shape at point without selection
    def checkShapeAtPoint(self, point: QPoint) -> bool:
        # Fast check if specified point is inside selected shape
        if self._selectedShape and self._selectedShape.isPointOnShape(point):
            return True

        # If not - check collection
        if self._shapesCollection.getShapeAtPoint(point):   
            return True
        else:
            return False

    # Try to change shape position, rollback if failed, return result
    def tryMoveSelectedShape(self, newPoint: QPoint) -> bool:
        # TODO: Add exception message
        if not self._selectedShape:
            raise NoCustomShapeSelected()

        oldPoint = self._selectedShape.centerPoint

        self._selectedShape.setNewCenterPoint(newPoint)

        # If collision check was successful - report success
        if self._collisionChecker.completeCollisionCheck(self._selectedShape):
            return True
        # Else - rollback changes and report failure
        else:
            self._selectedShape.setNewCenterPoint(oldPoint)
            return False

    # Overload for delta_x and delta_y
    def tryMoveSelectedShapeByDelta(self, delta_x: int, delta_y: int) -> bool:
        # TODO: Add exception message
        if not self._selectedShape:
            raise NoCustomShapeSelected()

        point = QPoint(self._selectedShape.centerPoint.x() + delta_x,
                       self._selectedShape.centerPoint.y() + delta_y)

        return self.tryMoveSelectedShape(point)

    # Try to create CustomRect using CustomShapeBaseFactory with center at specified position and report result
    # TODO: Better solution would be to accept CustomShape object from caller and delegate shape properties definition there
    def tryCreateShape(self, point: QPoint, factory: CustomShapeBaseFactory) -> bool:
        # Produce new shape via factory
        new_shape = factory.getNewCustomShape(point)

        # If shape fits in desired position - add it to collection, report result in any case
        if self._collisionChecker.completeCollisionCheck(new_shape):
            self._shapesCollection.addShape(new_shape)
            return True
        else:
            return False
        
    # Try to delete shape at specific point, returns true if success
    def tryDeleteShapeAtPoint(self, point: QPoint) -> bool:
        result = None

        # Check if currently selected shape (if any) is the shape to be deleted
        if self._selectedShape and self._selectedShape.isPointOnShape(point):
            result = self._selectedShape
            self.__deselectShape()
                
        # Search among other shapes only if selected one didn't get the result
        if not result:
            result = self._shapesCollection.getShapeAtPoint(point)

        if result:
            # Deletion of all related links
            # TODO: Should be optimized along with separate class for links, separate factory, etc.
            linksToDelete = []

            for link in self._shapeLinksCollection:
                if link._shape1 == result or link._shape2 == result:
                    linksToDelete.append(link)
                                         
            for link in linksToDelete:
                self._shapeLinksCollection.remove(link)

            self._shapesCollection.deleteShape(result)
            return True
        else:
            return False

    # Attempts to fins shape at point and link it with selected shape, reports result, clears selected shape after action
    def tryLinkWithSelectedShape(self, point: QPoint) -> bool:
        # TODO: Add exception message
        if not self._selectedShape:
            raise NoCustomShapeSelected()
        
        shape_2 = self._shapesCollection.getShapeAtPoint(point)

        if shape_2 and self._selectedShape != shape_2:
            self._shapeLinksCollection.append(ShapesLinkLine(self._selectedShape, shape_2))
            self.__deselectShape()
            return True
        
        else:
            return False

    # Clears stored geometry
    def clearGeometry(self) -> None:
        self._shapeLinksCollection.clear()
        self._shapesCollection.clearCollection()
        self._selectedShape = None

    # Draws saved geometry using provided QPainter
    def drawGeomerty(self, painter: QPainter) -> None:
        if self._selectedShape:
            self._selectedShape.drawCustomShape(painter)

        for rect in self._shapesCollection.shapesList:
            rect.drawCustomShape(painter)

        for link in self._shapeLinksCollection:
            link.drawLink(painter)

    # Internal method for proper selection removal and return selected shape to collection
    def __deselectShape(self) -> None:
        if self._selectedShape:
            self._shapesCollection.addShape(self._selectedShape)
            self._selectedShape = None

class NoCustomShapeSelected(Exception):
    pass