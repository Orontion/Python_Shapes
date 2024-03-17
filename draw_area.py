import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
from custom_rect import CustomRect, CustomRectRandomColorFactory
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
                new_shape = self._customRectFactory.getNewCustomRect(a0.pos())

                # TODO: Move shape check to other place
                if self._collisionChecker.completeCollisionCheck(new_shape):
                    self._shapesCollection.addShape(new_shape)
                    self.update()
                else:
                    print(f"Shape didn't pass collision check")
        
        return super().mouseDoubleClickEvent(a0)
    
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self._lastMousePos = a0.pos()
        result = self._shapesCollection.getShapeAtPoint(a0.pos())

        if result:
            print(f"MOUSEPRESSEVENT shape coords: {result.centerPoint.x()}, {result.centerPoint.y()}")

            match a0.button():
                case Qt.MouseButton.LeftButton:
                    self._movingShape = result
                    print("Ready to move")

        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        result = self._shapesCollection.getShapeAtPoint(a0.pos())

        match a0.button():
            case Qt.MouseButton.RightButton:
                pass

            case Qt.MouseButton.LeftButton:
                if self._moveStarted:
                    self._shapesCollection.addShape(self._movingShape)
                    self._movingShape = None
                    self._moveStarted = False
                else:
                    self._movingShape = None

            case Qt.MouseButton.MidButton:
                if result:
                    if self._shapeToLink:
                        if self._shapeToLink == result:
                            self._shapeToLink = None
                        else:
                            self._shapeLinksCollection.append(ShapesLinkLine(self._shapeToLink, result))
                            self._shapeToLink = None
                    else:
                        self._shapeToLink = result
                else:
                    self._shapeToLink = None

        return super().mouseReleaseEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        if self._movingShape:
            if not self._moveStarted:
                self._shapesCollection.deleteShape(self._movingShape)
                self._moveStarted = True
            
            self._rectToErase = self._movingShape

            # Simple logic for leaving window borders, should be changed on "leaving shape borders"
            delta_x = 0
            delta_y = 0

            if not (a0.x() < 0 or a0.x() > self.width()):
                delta_x = a0.x() - self._lastMousePos.x()
                
            if not (a0.y() < 0 or a0.y() > self.height()):
                delta_y = a0.y() - self._lastMousePos.y()

            self._lastMousePos = a0.pos()

            if self._collisionChecker.checkMovePossibility(self._movingShape, delta_x, delta_y):
                self._movingShape.setNewCenterPoint(delta_x, delta_y)

            self.update()

        return super().mouseMoveEvent(a0)
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        qp = QPainter(self)

        qp.eraseRect(0, 0, self.width(), self.height())

        for rect in self._shapesCollection.nodesList:
            rect.drawRect(qp)

        if self._movingShape and self._moveStarted:
            self._movingShape.drawRect(qp)

        for link in self._shapeLinksCollection:
            link.drawLink(qp)
        
        return super().paintEvent(a0)