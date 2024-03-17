import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
from custom_rect import CustomRect, CustomRectRandomColorFactory
from custom_shape import CustomShape
from positioning_helper_ineffective import ShapesCollection, CollisionProcessor
from shapes_link import ShapesLinkBase, ShapesLinkLine

class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)

        self._shapesCollection = ShapesCollection()
        self._collisionChecker = CollisionProcessor(self, self._shapesCollection)
        self._customRectFactory = CustomRectRandomColorFactory()
        self._movingShape: CustomRect = None
        self._moveStarted: bool = False
        self._rectToErase: CustomRect = None
        self._lastMousePos: QPoint = None
        self._shapeToLink: CustomRect = None
        self._newShapeRequested: bool = False
        self._shapeLinkingRequested: bool = False

        self._shapeLinksCollection: List[ShapesLinkBase] = []

        self.setLayout(QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight, None))

        self.setAutoFillBackground(True)
        palette = self.palette()

        palette.setColor(self.backgroundRole(), Qt.GlobalColor.gray)

        self.setPalette(palette)

    def switchColor(self) -> None:
        self.test_lbl.setText(f"Color check: {(self.palette().color(QPalette.ColorRole.Background) == Qt.GlobalColor.red)}")

        palette = self.palette()

        if palette.color(QPalette.ColorRole.Background) == Qt.GlobalColor.red:
            palette.setColor(QPalette.ColorRole.Background, Qt.GlobalColor.green)
        else:
            palette.setColor(QPalette.ColorRole.Background, Qt.GlobalColor.red)

        self.setPalette(palette)

    # Double click
    def mouseDoubleClickEvent(self, a0: QMouseEvent | None) -> None:
        match a0.button():
            case Qt.MouseButton.RightButton:
                result = self._shapesCollection.getShapeAtPoint(a0.pos())

                if result:
                    self._rectToErase = result
                    self._shapesCollection.deleteShape(result)
                    self.update()
            
            case Qt.MouseButton.LeftButton:
                self.tryCreateRect(a0.pos())
        
        return super().mouseDoubleClickEvent(a0)
    
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self._lastMousePos = a0.globalPos()

        match a0.button():
            case Qt.MouseButton.LeftButton:
                if self._newShapeRequested:
                    self.tryCreateRect(a0.pos())
                    self._newShapeRequested = False
                elif self._shapeLinkingRequested:
                    pass
                else:
                    result = self._shapesCollection.getShapeAtPoint(a0.pos())
                    self._movingShape = result

        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        self._lockCursor = False
        result = self._shapesCollection.getShapeAtPoint(a0.pos())

        match a0.button():
            case Qt.MouseButton.RightButton:
                pass

            case Qt.MouseButton.LeftButton:
                if self._shapeLinkingRequested:
                    self.selectShapeForLinking(result)
                if self._moveStarted:
                    self._shapesCollection.addShape(self._movingShape)
                    self._movingShape = None
                    self._moveStarted = False
                else:
                    self._movingShape = None

            case Qt.MouseButton.MidButton:
                self.selectShapeForLinking(result)

        return super().mouseReleaseEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        delta_x = a0.globalPos().x() - self._lastMousePos.x()
        delta_y = a0.globalPos().y() - self._lastMousePos.y()

        if self.processMoveAction(delta_x, delta_y):
            self._lastMousePos = a0.globalPos()
            self.update()
        else:
            self.cursor().setPos(self._lastMousePos)

        return super().mouseMoveEvent(a0)
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        qp = QPainter(self)

        # Clear painting area
        qp.eraseRect(0, 0, self.width(), self.height())

        # Draw shapes
        for rect in self._shapesCollection.nodesList:
            rect.drawCustomShape(qp)

        # Draw currentrly moving shape separately - it is removed from collection while moving
        if self._movingShape and self._moveStarted:
            self._movingShape.drawCustomShape(qp)

        # Draw links
        for link in self._shapeLinksCollection:
            link.drawLink(qp)
        
        return super().paintEvent(a0)
    
    def processMoveAction(self, delta_x: int, delta_y: int) -> bool:
        if self._movingShape:
            if not self._moveStarted:
                self._shapesCollection.deleteShape(self._movingShape)
                self._moveStarted = True

            new_point = QPoint(self._movingShape.centerPoint.x() + delta_x,
                               self._movingShape.centerPoint.y() + delta_y)

            return self.tryMoveShape(self._movingShape, new_point)
        
        return True

    def tryMoveShape(self, shape: CustomShape, newPoint: QPoint) -> bool:
        oldPoint = shape.centerPoint

        shape.setNewCenterPoint(newPoint)

        if self._collisionChecker.completeCollisionCheck(shape):
            return True
        else:
            shape.setNewCenterPoint(oldPoint)
            return False
        
    def tryCreateRect(self, point: QPoint) -> bool:
        new_shape = self._customRectFactory.getNewCustomRect(point)

        if self._collisionChecker.completeCollisionCheck(new_shape):
            self._shapesCollection.addShape(new_shape)
            self.update()
            return True
        else:
            return False
        
    def selectShapeForLinking(self, shape: CustomShape) -> None:
        # TODO: Refine if sequense
        if shape:
            if self._shapeToLink:
                if self._shapeToLink == shape:
                    self._shapeToLink = None
                    self._shapeLinkingRequested = False
                else:
                    self._shapeLinksCollection.append(ShapesLinkLine(self._shapeToLink, shape))
                    self._shapeToLink = None
                    self._shapeLinkingRequested = False
                    self.update()
            else:
                self._shapeToLink = shape
        else:
            self._shapeToLink = None
            self._shapeLinkingRequested = False

    def startRectCreation(self) -> None:
        self._newShapeRequested = True

    def startLinkCreation(self) -> None:
        self._shapeLinkingRequested = True

    def clearArea(self) -> None:
        self._shapeLinksCollection.clear()
        self._shapesCollection.clearCollection()
        self.update()