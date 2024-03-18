from typing import Union, List
from enum import Enum

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtCore import Qt, QPoint

from custom_rect import CustomRect, CustomRectRandomColorFactory
from custom_shape import CustomShape
from positioning_helper_ineffective import ShapesCollection, CollisionProcessor
from shapes_link import ShapesLinkBase, ShapesLinkLine

class DrawAreaActions(Enum):
    DELETE_SHAPE = 1
    CREATE_RECT_AT_POINT = 2
    CREATE_LINK = 3
    SELECT_FOR_MOVE = 4
    MOVE_TO_POINT = 5
    SHAPE_DRAG = 6

class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)

        # TODO: Should be moved to separate shape processing class
        # Collections for shapes and links
        self._shapesCollection = ShapesCollection()
        self._shapeLinksCollection: List[ShapesLinkBase] = []           # TODO: Should restrict duplicate link creation (WHAT IS a duplicate link?)

        # Checker for collisions
        self._collisionChecker = CollisionProcessor(self, self._shapesCollection)
        self._customRectFactory = CustomRectRandomColorFactory()
        self._shapeToDrag: CustomRect = None
        self._shapeForMove: CustomRect = None
        self._shapeToLink: CustomRect = None

        # End of properties to move ==========

        # Last mouse position to keep it on the shape if it cannot be moved
        self._lastMousePos: QPoint = None
        # Current action being performed - it is used to determine what to do with click
        self._currentAction: DrawAreaActions = None

        # Set background color to gray
        # TODO: Configurable background?
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.gray)
        self.setPalette(palette)

    # Double click
    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        match a0.button():
            # Doubleclick with RMB - delete shape under cursor
            case Qt.MouseButton.RightButton:
                self.tryDeleteRect(a0.pos())
            
            # Doubleclick with LMB - create shape with center under cursor
            case Qt.MouseButton.LeftButton:
                self.tryCreateRect(a0.pos())
        
        return super().mouseDoubleClickEvent(a0)
    
    # Mouse button press
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        # Save cursor position as global to handle keeping cursor on shape
        self._lastMousePos = a0.globalPos()

        match a0.button():
            case Qt.MouseButton.LeftButton:
                match self._currentAction:
                    # Default action - find shape (or it's absense) under the cursor and mark it as shape for move
                    case _ :
                        result = self._shapesCollection.getShapeAtPoint(a0.pos())
                        self._shapeToDrag = result

        return super().mousePressEvent(a0)

    # Mouse button release
    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        match a0.button():
            # Left button behavior depends on current action
            # Most of this is intended to be used with toolbar/context menus
            # E.g. "Move shape" button -> click on shape -> click where to move selected shape
            case Qt.MouseButton.LeftButton:
                match self._currentAction:
                    # Create rectangle with center at cursor after single click
                    case DrawAreaActions.CREATE_RECT_AT_POINT:
                        self.tryCreateRect(a0.pos())
                        self._currentAction = None
                    # Link creation process - either first or second click
                    case DrawAreaActions.CREATE_LINK:
                        self.performShapeLinking(a0.pos())
                    # Delete shape under cursor
                    case DrawAreaActions.DELETE_SHAPE:
                        self.tryDeleteRect(a0.pos())
                    # Select shape to move to specific point
                    case DrawAreaActions.SELECT_FOR_MOVE:
                        self._shapeForMove = self._shapesCollection.getShapeAtPoint(a0.pos())
                        self._currentAction = DrawAreaActions.MOVE_TO_POINT
                    # Try to move selected shape to selected point
                    case DrawAreaActions.MOVE_TO_POINT:
                        self.moveShapeToPosition(self._shapeForMove, a0.pos())
                        self._shapeForMove = None
                        self._currentAction = None
                    # End of shape drag process - add moved shape back to collection,
                    # clear variables
                    case DrawAreaActions.SHAPE_DRAG:
                        self._shapesCollection.addShape(self._shapeToDrag)
                        self._shapeToDrag = None
                        self._currentAction = None
                    # If no action specified - clear temp variable in case user pressed on some shape
                    case _:
                        self._shapeToDrag = None

            # MMB single click is being used to link shapes
            case Qt.MouseButton.MidButton:
                self.performShapeLinking(a0.pos())

        return super().mouseReleaseEvent(a0)
    
    # Mouse move
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        # Calculate deltas to properly drag shape
        delta_x = a0.globalPos().x() - self._lastMousePos.x()
        delta_y = a0.globalPos().y() - self._lastMousePos.y()

        # If shape has been moved - update cursor position
        if self.processDragAction(delta_x, delta_y):
            self._lastMousePos = a0.globalPos()
            self.update()
        # If shape met obstacle - keep cursor locked in place with the shape
        else:
            self.cursor().setPos(self._lastMousePos)

        return super().mouseMoveEvent(a0)
    
    # Widget painting
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        # Define painter
        qp = QPainter(self)

        # Clear painting area
        qp.eraseRect(0, 0, self.width(), self.height())

        # Draw shapes
        for rect in self._shapesCollection.nodesList:
            rect.drawCustomShape(qp)

        # Draw currentrly moving shape separately - it is removed from collection while moving
        if self._shapeToDrag and self._currentAction == DrawAreaActions.SHAPE_DRAG:
            self._shapeToDrag.drawCustomShape(qp)

        # Draw links
        for link in self._shapeLinksCollection:
            link.drawLink(qp)
        
        return super().paintEvent(a0)
    
    # Moving shape via dragging and return operation result
    def processDragAction(self, delta_x: int, delta_y: int) -> bool:
        # Do drag only if some shape is selected for dragging
        if self._shapeToDrag:
            # Move widget to SHAPE_DRAG mode if it wasn't
            # Delete shape from all shape collection - old logic used to properly search and rebuild KD-Tree
            # KD-Tree wasn't implemented, but logic left for future re-use
            if self._currentAction != DrawAreaActions.SHAPE_DRAG:
                self._shapesCollection.deleteShape(self._shapeToDrag)
                self._currentAction = DrawAreaActions.SHAPE_DRAG

            # Define new center point for shape based on X and Y deltas
            new_point = QPoint(self._shapeToDrag.centerPoint.x() + delta_x,
                               self._shapeToDrag.centerPoint.y() + delta_y)

            # Try to move shape and report result
            return self.tryMoveShape(self._shapeToDrag, new_point)
        
        # Default is True to avoid cursor blocking
        return True

    # Simple shape move to specified position with widget refresh
    def moveShapeToPosition(self, shape: CustomShape, newPoint: QPoint) -> None:
        # Same logic as in processDragAction() for compatibility
        self._shapesCollection.deleteShape(shape)
        self.tryMoveShape(shape, newPoint)
        self._shapesCollection.addShape(shape)
        self.update()

    # Try to change shape position, rollback if failed, return result
    def tryMoveShape(self, shape: CustomShape, newPoint: QPoint) -> bool:
        oldPoint = shape.centerPoint

        shape.setNewCenterPoint(newPoint)

        # If collision check was successful - report success
        if self._collisionChecker.completeCollisionCheck(shape):
            return True
        # Else - rollback changes and report failure
        else:
            shape.setNewCenterPoint(oldPoint)
            return False

    # Try to create shape with center at specified position and report result    
    def tryCreateRect(self, point: QPoint) -> bool:
        # Produce new shape via factory
        new_shape = self._customRectFactory.getNewCustomRect(point)

        # If shape fits in desired position - add it to collection, report result in any case
        if self._collisionChecker.completeCollisionCheck(new_shape):
            self._shapesCollection.addShape(new_shape)
            self.update()
            return True
        else:
            return False

    # Try to delete shape at specific point
    def tryDeleteRect(self, point: QPoint) -> None:
        result = self._shapesCollection.getShapeAtPoint(point)

        if result:
            self._shapesCollection.deleteShape(result)
            self.update()

    # Links shapes at selected point
    # TODO: Rework method, it is too inconsistent with the rest of design
    def performShapeLinking(self, point: QPoint) -> None:
        # TODO: Refine if sequense
        shape = self._shapesCollection.getShapeAtPoint(point)

        if shape:
            if self._shapeToLink:
                if self._shapeToLink == shape:
                    self._shapeToLink = None
                    self._currentAction = None
                else:
                    self._shapeLinksCollection.append(ShapesLinkLine(self._shapeToLink, shape))
                    self._shapeToLink = None
                    self._currentAction = None
                    self.update()
            else:
                self._shapeToLink = shape
        else:
            self._shapeToLink = None
            self._currentAction = None

    # Slot which starts rectangle creation by single click
    def startRectCreation(self) -> None:
        self._currentAction = DrawAreaActions.CREATE_RECT_AT_POINT

    # Slot which starts link creation by LMB clicks
    def startLinkCreation(self) -> None:
        self._currentAction = DrawAreaActions.CREATE_LINK

    # Slot which starts rectangle move by pointing the new location
    def startRectMove(self) -> None:
        self._currentAction = DrawAreaActions.SELECT_FOR_MOVE

    # Slot which starts deletion of shape by LMB click
    def deleteShape(self) -> None:
        self._currentAction = DrawAreaActions.DELETE_SHAPE

    # Slot and method which clears the draw area
    def clearArea(self) -> None:
        self._shapeLinksCollection.clear()
        self._shapesCollection.clearCollection()
        self.update()