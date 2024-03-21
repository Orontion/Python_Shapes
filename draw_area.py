from typing import Union, List
from enum import Enum, auto

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter
from PyQt5.QtCore import Qt, QPoint

from custom_rect import CustomRectRandomColorFactory

from shapes_link import ShapesLinkBase, ShapesLinkLine
from geometry_controller import GeometryController

class DrawAreaActions(Enum):
    NO_ACTION = auto()
    DELETE_SHAPE = auto()
    CREATE_RECT_AT_POINT = auto()
    SELECT_FOR_LINKING_LMB = auto()
    CREATE_LINK_LMB = auto()
    CREATE_LINK_MMB = auto()
    SELECT_FOR_MOVE = auto()
    MOVE_TO_POINT = auto()
    SHAPE_SELECTED_FOR_DRAG = auto()
    SHAPE_DRAG = auto()

class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)

        # Geometry controller handles shapes behavior logic
        self._geometryController = GeometryController(self)

        # Creates rectangles with random colors
        self._customRectFactory = CustomRectRandomColorFactory()

        # Last mouse position to keep it on the shape if it cannot be moved
        self._lastMousePos: QPoint = None
        # Current action being performed - it is used to determine what to do with click
        self._currentAction: DrawAreaActions = DrawAreaActions.NO_ACTION

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
                self._geometryController.tryDeleteShapeAtPoint(a0.pos())
                self.update()
            
            # Doubleclick with LMB - create shape with center under cursor
            case Qt.MouseButton.LeftButton:
                # Doubleclick resets any started actions
                self.__resetCurrentAction()

                self._geometryController.tryCreateShape(a0.pos(), self._customRectFactory)
                self.update()
        
        return super().mouseDoubleClickEvent(a0)
    
    # Mouse button press
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        # Save cursor position as global to handle keeping cursor on shape
        self._lastMousePos = a0.globalPos()

        match a0.button():
            case Qt.MouseButton.LeftButton:
                clickedOnShape = self._geometryController.checkShapeAtPoint(a0.pos())

                match self._currentAction:
                    # If there were no actions, or user was creating link via MMB - try to switch to shape drag
                    case DrawAreaActions.NO_ACTION | DrawAreaActions.CREATE_LINK_MMB :
                        # Switch to drag only if click was on shape, select this shape for dragging
                        if clickedOnShape:
                            self._geometryController.trySelectShape(a0.pos())
                            self._currentAction = DrawAreaActions.SHAPE_SELECTED_FOR_DRAG

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
                        self._geometryController.tryCreateShape(a0.pos(), self._customRectFactory)
                        self._currentAction = DrawAreaActions.NO_ACTION
                        self.update()
                    # Link creation process - start link creation via LMB
                    case DrawAreaActions.SELECT_FOR_LINKING_LMB:
                        if self.__beginLinkCreation(a0.pos()):
                            self._currentAction = DrawAreaActions.CREATE_LINK_LMB
                    # Link creation process - end link creation via LMB
                    case DrawAreaActions.CREATE_LINK_LMB:
                        if self.__finishLinkCreation(a0.pos()):
                            self._currentAction = DrawAreaActions.NO_ACTION
                            self.update()
                    # Delete shape under cursor
                    case DrawAreaActions.DELETE_SHAPE:
                        self._geometryController.tryDeleteShapeAtPoint(a0.pos())
                        self._currentAction = DrawAreaActions.NO_ACTION
                        self.update()
                    # Select shape to move to specific point
                    # Selection mode remains active until the shape is selected
                    case DrawAreaActions.SELECT_FOR_MOVE:
                        if self._geometryController.trySelectShape(a0.pos()):
                            self._currentAction = DrawAreaActions.MOVE_TO_POINT
                    # Try to move selected shape to selected point, unselect shape after attempt
                    case DrawAreaActions.MOVE_TO_POINT:
                        self._geometryController.tryMoveSelectedShape(a0.pos())
                        self._geometryController.clearSelectedShape()
                        self._currentAction = DrawAreaActions.NO_ACTION
                        self.update()
                    # End of shape drag process
                    case DrawAreaActions.SHAPE_DRAG:
                        self._currentAction = DrawAreaActions.NO_ACTION
                        self.update()
                    # If no action specified - clear actions
                    case _:
                        self._currentAction = DrawAreaActions.NO_ACTION

            # MMB single click is being used to link shapes
            case Qt.MouseButton.MidButton:
                match self._currentAction:
                    # Second MMB click - create link
                    case DrawAreaActions.CREATE_LINK_MMB:
                        if self.__finishLinkCreation(a0.pos()):
                            self._currentAction = DrawAreaActions.NO_ACTION
                            self.update()
                    # No actions specified and first MMB click - start link creation via MMB
                    case DrawAreaActions.NO_ACTION:
                        if self.__beginLinkCreation(a0.pos()):
                            self._currentAction = DrawAreaActions.CREATE_LINK_MMB

            # RMB resets any current action
            case Qt.MouseButton.RightButton:
                self.__resetCurrentAction()

        return super().mouseReleaseEvent(a0)
    
    # Mouse move
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        # Calculate deltas to properly drag shape
        delta_x = a0.globalPos().x() - self._lastMousePos.x()
        delta_y = a0.globalPos().y() - self._lastMousePos.y()

        # If shape has been moved - update cursor position
        if self.__processDragAction(delta_x, delta_y):
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

        # Draw current geometry
        self._geometryController.drawGeomerty(qp)
        
        return super().paintEvent(a0)
    
    # Moving shape via dragging and return operation result
    def __processDragAction(self, delta_x: int, delta_y: int) -> bool:
        # If shape was selected for drag - start dragging process
        if self._currentAction == DrawAreaActions.SHAPE_SELECTED_FOR_DRAG:
            self._currentAction = DrawAreaActions.SHAPE_DRAG

        # If dragging is in progress - try update the shape position
        if self._currentAction == DrawAreaActions.SHAPE_DRAG:
            return self._geometryController.tryMoveSelectedShapeByDelta(delta_x, delta_y)
        
        # Default is True to avoid cursor blocking
        return True

    # Internal method to properly start link creation
    def __beginLinkCreation(self, point: QPoint) -> bool:
        return self._geometryController.trySelectShape(point)

    # Internal method to properly finish link creation
    def __finishLinkCreation(self, point: QPoint) -> bool:
        return self._geometryController.tryLinkWithSelectedShape(point)

    # Internal method to reset current actions
    def __resetCurrentAction(self) -> None:
        self._currentAction = DrawAreaActions.NO_ACTION
        self._geometryController.clearSelectedShape()

    # Slot which starts rectangle creation by single click
    def startRectCreation(self) -> None:
        self._currentAction = DrawAreaActions.CREATE_RECT_AT_POINT
        self._geometryController.clearSelectedShape()

    # Slot which starts link creation by LMB clicks
    def startLinkCreation(self) -> None:
        self._currentAction = DrawAreaActions.SELECT_FOR_LINKING_LMB
        self._geometryController.clearSelectedShape()

    # Slot which starts rectangle move by pointing the new location
    def startRectMove(self) -> None:
        self._currentAction = DrawAreaActions.SELECT_FOR_MOVE
        self._geometryController.clearSelectedShape()

    # Slot which starts deletion of shape by LMB click
    def deleteShape(self) -> None:
        self._currentAction = DrawAreaActions.DELETE_SHAPE
        self._geometryController.clearSelectedShape()

    # Slot and method which clears the draw area
    def clearArea(self) -> None:
        self._geometryController.clearGeometry()
        self._geometryController.clearSelectedShape()
        self.update()