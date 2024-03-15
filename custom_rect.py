import sys

from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPainter, QPalette, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

import constants

class CustomRect(QRect):
    def __init__(self, centerPoint: QPoint, size: QSize, color: QColor) -> None:
        self._centerPoint = centerPoint
        self._size = size
        self._color = color

        super().__init__(CustomRect.calculateAnchorPoint(centerPoint, size), self._size)

    @property
    def centerPoint(self) -> QPoint:
        return self._centerPoint
    
    @property
    def color(self) -> QColor:
        return self._color

    def calculateAnchorPoint(centerPoint: QPoint, size: QSize) -> QPoint:
        min_x = centerPoint.x() - size.width() // 2

        min_y = centerPoint.y() - size.height() // 2

        # Check for negative numbers?

        return QPoint(min_x, min_y)