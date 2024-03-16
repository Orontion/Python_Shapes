import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize

import constants
from custom_rect import CustomRect
from positioning_helper import ShapeNode, ShapeNodesCollection

class DrawArea(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget = None, flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)

        self._shapeNodesCollection = ShapeNodesCollection()
        self.setLayout(QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.LeftToRight, None))

        self._rects: List[CustomRect] = []

        self.test_lbl = QtWidgets.QLabel()
        self.test_lbl.setText("Test")
        self.layout().addWidget(self.test_lbl)

        self.setAutoFillBackground(True)
        palette = self.palette()

        palette.setColor(self.backgroundRole(), Qt.GlobalColor.red)

        self.setPalette(palette)

    def refreshSize(self) -> None:
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
        if self.areaBorderCheck(new_shape):
            result = self._shapeNodesCollection.searchNearestNode(new_shape.centerPoint)

            if result:
                print(f"Closest shape center point coordinates: x{result.centerPoint.x()}, y{result.centerPoint.y()}")
                if not result.intersects(new_shape):
                    self._rects.append(new_shape)
                    self._shapeNodesCollection.addNode(new_shape)
                    self.update()
                else:
                    print(f"New shape intersects with existing one!")
            else:
                self._rects.append(new_shape)
                self._shapeNodesCollection.addNode(new_shape)
                self.update()
        else:
            print(f"Shape is out of bounds:")

        return super().mouseDoubleClickEvent(a0)
    
    # Check if new shape fits into draw area
    def areaBorderCheck(self, shape: CustomRect) -> bool:
        if shape.top() < 0 or shape.left() < 0:
            return False

        if shape.bottom() > self.size().height() or shape.right() > self.size().width():
            return False
        
        return True
    
    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        result = self._shapeNodesCollection.searchNearestNode(a0.pos())

        if result:
            print(f"Closest shape is at coords: {result.centerPoint.x()}, {result.centerPoint.y()}")

            if result.contains(a0.pos()):
                print(f"Clicked inside of the shape!")

        return super().mousePressEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:

        if a0.button() == Qt.MouseButton.MidButton:
            self.switchColor()

        return super().mouseReleaseEvent(a0)
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        qp = QPainter(self)

        for rect in self._rects:
            qp.setPen(Qt.GlobalColor.black)
            qp.drawRect(rect)
        
        return super().paintEvent(a0)