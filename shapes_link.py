from abc import ABC, abstractmethod

from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

from custom_rect import CustomRect

# Base class for link between shapes
# Contains shapes which specific link connects
class ShapesLinkBase(ABC):
    @abstractmethod
    def __init__(self, shape_1: CustomRect, shape_2: CustomRect) -> None:
        self._shape1 = shape_1
        self._shape2 = shape_2
        super().__init__()

    # Defines how link is being drawn
    @abstractmethod
    def drawLink(self, painter: QPainter) -> None:
        pass

# Link in for of simple line, no specific properties
class ShapesLinkLine(ShapesLinkBase):
    def __init__(self, shape_1: CustomRect, shape_2: CustomRect) -> None:
        super().__init__(shape_1, shape_2)

    def drawLink(self, painter: QPainter) -> None:
        point1 = self._shape1.getLinkPoint(self._shape2)
        point2 = self._shape2.getLinkPoint(self._shape1)

        painter.setPen(Qt.GlobalColor.black)
        painter.drawLine(point1, point2)