from random import randint
from math import ceil

from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize

import constants
from custom_shape import CustomShape, CustomShapeBaseFactory

# CustomRect has additional Color property
class CustomRect(CustomShape):
    def __init__(self, centerPoint: QPoint, size: QSize, color: QColor) -> None:
        self._size = size
        self._color = color
        self._geometryObject = QRect(CustomRect.__calculateAnchorPoint(centerPoint, size), self._size)
        super().__init__(centerPoint, self._geometryObject)

    @property
    def color(self) -> QColor:
        return self._color

    # Internal method to calculate top-left corner of rectangle based on provided center point
    def __calculateAnchorPoint(centerPoint: QPoint, size: QSize) -> QPoint:
        # Calculation formula matches QRect result for center and top-left corner
        min_x = ceil(centerPoint.x() - (size.width() - 1) / 2)
        min_y = ceil(centerPoint.y() - (size.height() -1) / 2)

        return QPoint(min_x, min_y)
    
    # Sets new center point and moves the shape accordingly
    def setNewCenterPoint(self, point: QPoint) -> None:
        self._centerPoint = point
        self._geometryObject.moveCenter(self._centerPoint)

    # Returns optimal point to start the link to specified shape
    def getLinkPoint(self, shape: CustomShape) -> QPoint:
        linkPoint = QPoint()

        # Initially deltas between shape borders are 0
        borderDeltaX = 0
        borderDeltaY = 0

        # Calculate delta between closest vertical borders of shapes
        # if closest vertical border of shape 2 is located between left and right borders of current shape - delta is 0
        if shape.centerPoint.x() > self.centerPoint.x():
            if shape.getBottomLeftBound().x() > self.getBottomRightBound().x():
                borderDeltaX = shape.getBottomLeftBound().x() - self.getBottomRightBound().x()
        else:
            if shape.getBottomRightBound().x() < self.getBottomLeftBound().x():
                borderDeltaX = shape.getBottomRightBound().x() - self.getBottomLeftBound().x()

        # Same calculation for vertical borders
        if shape.centerPoint.y() > self.centerPoint.y():
            if shape.getTopRightBound().y() > self.getBottomRightBound().y():
                borderDeltaY = shape.getTopRightBound().y() - self.getBottomRightBound().y()
        else:
            if shape.getBottomRightBound().y() < self.getTopRightBound().y():
                borderDeltaY = shape.getBottomRightBound().y() - self.getTopRightBound().y()

        # Select biggest delta to make angle between edge and link as close to 90 degrees as possible
        if abs(borderDeltaX) > abs(borderDeltaY):
            # If biggest delta is on X, then plase the point in the middle of side enge usin center point's Y coord
            linkPoint.setY(self._centerPoint.y())

            # Place point on closest side to target shape
            if borderDeltaX > 0:
                linkPoint.setX(self.getBottomRightBound().x())
            else:
                linkPoint.setX(self.getBottomLeftBound().x())
        
        # Same for other axis
        else:
            linkPoint.setX(self._centerPoint.x())

            if borderDeltaY > 0:
                linkPoint.setY(self.getBottomRightBound().y())
            else:
                linkPoint.setY(self.getTopRightBound().y())

        return linkPoint

    # Draw shape - for CustomRect it is just a rectangle without borders and with specific fill color
    def drawCustomShape(self, painter: QPainter) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.color)
        painter.drawRect(self._geometryObject)

    # Boundary intersection check
    def checkIntersectionBoundary(self, shape: CustomShape) -> bool:
        return self._boundaryRect.intersects(shape.boundaryRect)
    
    # Precise intersection check
    # TODO: For now it is simplified to be same as boundary
    def checkIntersectionPrecise(self, shape: CustomShape) -> bool:
        return self._boundaryRect.intersects(shape.boundaryRect)

    # Check if point is located on shape
    def isPointOnShape(self, point: QPoint) -> bool:
        return self._geometryObject.contains(point)

# Basic factory class
# For base class default color and size are defined in constants
class CustomRectBaseFactory(CustomShapeBaseFactory):
    def __init__(self) -> None:
        self._defaultSize: QSize = QSize(constants.RECT_SIZE_X, constants.RECT_SIZE_Y)
        self.__defaultColor: QColor = constants.RECT_DEFAULT_COLOR
        super().__init__()

    def getNewCustomRect(self, centerPoint: QPoint, size: QSize, color: QColor) -> CustomRect:
        return CustomRect(centerPoint, size, color)
    
    def getNewCustomShape(self, centerPoint: QPoint) -> CustomRect:
        return CustomRect(centerPoint, self._defaultSize, self.__defaultColor)
    
# Factory which produces rectangles with random colors
# TODO: Make color table configurable
class CustomRectRandomColorFactory(CustomRectBaseFactory):
    def __init__(self) -> None:
        self.__colorTable = (Qt.GlobalColor.red,
                             Qt.GlobalColor.green,
                             Qt.GlobalColor.blue,
                             Qt.GlobalColor.yellow)
        super().__init__()

    # Instead of default color returns random color, still uses default size
    def getNewCustomShape(self, centerPoint: QPoint) -> CustomRect:
        color = self.__colorTable[randint(0, len(self.__colorTable) - 1)]
        return CustomRect(centerPoint, self._defaultSize, color)