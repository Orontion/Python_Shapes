import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
from custom_rect import CustomRect
from positioning_helper_ineffective import ShapesCollection, CollisionProcessor

class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)

        self._shapesCollection = ShapesCollection()
        self._collisionChecker = CollisionProcessor(self, self._shapesCollection)
        self._movingShape: CustomRect = None
        self._moveStarted: bool = False
        self._rectToErase: CustomRect = None
        self._lastMousePos: QPoint = None

        self.setLayout(QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight, None))

        self.test_lbl = QtWidgets.QLabel()
        self.test_lbl.setText("Test")
        self.layout().addWidget(self.test_lbl)

        self.setAutoFillBackground(True)
        palette = self.palette()

        palette.setColor(self.backgroundRole(), Qt.GlobalColor.red)

        self.setPalette(palette)

    def refreshSize(self) -> None:
        self._collisionChecker._drawingWidget = self.size()
        self.test_lbl.setText(f"NEW Height: {str(self.height())}; Width: {str(self.width())}")

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
        print(f"Double click catched")
        current_point = a0.localPos().toPoint()

        # TODO: Move shape generation to separate method
        new_shape = CustomRect(current_point,
                               QSize(constants.RECT_SIZE_X, constants.RECT_SIZE_Y),
                               Qt.GlobalColor.blue)

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
                if result:
                    self._rectToErase = result
                    self._shapesCollection.deleteShape(result)
                    self.update()

            case Qt.MouseButton.LeftButton:
                if self._moveStarted:
                    self._shapesCollection.addShape(self._movingShape)
                    self._movingShape = None
                    self._moveStarted = False
                else:
                    self._movingShape = None

            case Qt.MouseButton.MidButton:
                self.switchColor()

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

        for rect in self._shapesCollection.nodesList:
            qp.setPen(Qt.GlobalColor.black)
            qp.drawRect(rect)

        if self._rectToErase:
            qp.eraseRect(self._rectToErase)
            self._rectToErase = None

        if self._movingShape and self._moveStarted:
            qp.setPen(Qt.GlobalColor.black)
            qp.drawRect(self._movingShape)
        
        return super().paintEvent(a0)