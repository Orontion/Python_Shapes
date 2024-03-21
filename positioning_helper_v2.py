from typing import List

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QPoint

from custom_shape import CustomShape

# Class with custom shapes collection
# Main goals: store all shapes on a plane, add/modify/delete shapes,
# effectively search for a shape at certain point
# effectively search for nearest shape(s) to point/to shape
#
# Uses simple binary search through sorted array of shapes bounding boxes edge points
# to quickly find intersections between bounding boxes
class ShapesCollection():
    def __init__(self) -> None:
        self._shapesList: List[CustomShape] = []
        self._nodeBoundaryPointsList: List[tuple] = []          # TODO: This tuple ideally should be of specific class
        # This value is used to restict search for point intersections
        self._shapeMaxWidth = 0

    @property
    def shapesList(self) -> List[CustomShape]:
        return self._shapesList

    # Add shape to collection and update necessary metadata
    def addShape(self, shape: CustomShape) -> None:
        self._shapesList.append(shape)

        if (len(self._nodeBoundaryPointsList) > 0):
            indexToInsert = self.__findClosestBoundaryPointIndex(shape.getTopLeftBound().x()) + 1

            # TODO: Refine this to separate method
            # Bump index in edge case when __findClosestBoundaryPointIndex returned 0
            # There could be no "more left" point in collection (see search method comments)
            # Or index 0 could be actual result
            # In insertion case it is critical, so distinguish it by result verification
            if indexToInsert == 1:
                if self._nodeBoundaryPointsList[indexToInsert][0].x() >= shape.getTopLeftBound().x():
                    indexToInsert -= 1

            self._nodeBoundaryPointsList.insert(indexToInsert, (shape.getTopLeftBound(), shape))

            indexToInsert = self.__findClosestBoundaryPointIndex(shape.getBottomRightBound().x()) + 1

            if indexToInsert == 0:
                if self._nodeBoundaryPointsList[1][0].x() >= shape.getTopLeftBound().x():
                    indexToInsert += 1

            self._nodeBoundaryPointsList.insert(indexToInsert, (shape.getBottomRightBound(), shape)) 
            # If collection is empty - add first points
        else:
            self._nodeBoundaryPointsList.append((shape.getTopLeftBound(), shape))
            self._nodeBoundaryPointsList.append((shape.getBottomRightBound(), shape))

        # Update maximal shape width for optimized search
        if shape.boundaryRect.width() > self._shapeMaxWidth:
            self._shapeMaxWidth = shape.boundaryRect.width()

    # Returns shape at specific point or None, if shape was not found
    def getShapeAtPoint(self, point: QPoint) -> CustomShape:
        possibleShapes = self.__getBoundaryIntersectedShapesListAtPoint(point)

        # Several shapes could intersect their boundary rects, but could be not overlapped by other shape itself
        # However, only 1 shape could contain the point, so if we found one - return it
        for shape in possibleShapes:
            if shape.isPointOnShape(point):
                return shape

        return None
    
    # Removes shape from collection at specific point and returns it as result
    # or returns None, if shape was not found
    def popShapeAtPoint(self, point: QPoint) -> CustomShape:
        result = self.getShapeAtPoint(point)

        if result:
            self.deleteShape(result)
            return result
        else:
            return None

    # Gets set of shapes which bounding boxes intersect with bounding box of specified shape
    def getBoundaryIntersectedShapesSet(self, shape: CustomShape) -> set[CustomShape]:
        result = self.__getBoundaryIntersectedShapesListAtPoint(shape.getTopLeftBound())
        result.update(self.__getBoundaryIntersectedShapesListAtPoint(shape.getBottomLeftBound()))

        return result

    # Removes shape from the collection
    def deleteShape(self, shape: CustomShape) -> None:
        pointsToDelete = []

        # Find starting point of shape
        startingIndex = self.__findClosestBoundaryPointIndex(shape.getTopLeftBound().x())

        # Handle empty collection case
        if startingIndex == -1:
            return

        # Find both shape points (there can be only two in a collection at a time)
        for point in range(startingIndex, len(self._nodeBoundaryPointsList)):
            if self._nodeBoundaryPointsList[point][1] == shape:
                pointsToDelete.append(self._nodeBoundaryPointsList[point])
            # When both found - stop
            if len(pointsToDelete) == 2:
                break
        
        # Remove found points
        for point in pointsToDelete:
            self._nodeBoundaryPointsList.remove(point)

        # Remove shape
        self._shapesList.remove(shape)

    # Returns index of "first" (or "most left") boundary point in list with X lesser than specified value
    # Returns -1 if _nodeBoundaryPointsList is empty
    def __findClosestBoundaryPointIndex(self, x: int) -> int:
        if len(self._nodeBoundaryPointsList) == 0:
            return -1

        # Start binary search
        searchFinished = False
        previousIndexBegin = 0
        previousIndexEnd = len(self._nodeBoundaryPointsList) - 1
        searchIndex = (len(self._nodeBoundaryPointsList) -1) // 2

        while not searchFinished:
            if self._nodeBoundaryPointsList[searchIndex][0].x() > x:
                if searchIndex == previousIndexBegin:
                    searchFinished = True
                previousIndexEnd = searchIndex
                searchIndex = previousIndexBegin + ((previousIndexEnd - previousIndexBegin) // 2)
            
            elif self._nodeBoundaryPointsList[searchIndex][0].x() < x:
                if searchIndex == previousIndexBegin:
                    searchFinished = True
                previousIndexBegin = searchIndex
                searchIndex = previousIndexBegin + ((previousIndexEnd - previousIndexBegin) // 2)
                
            else:
                searchFinished = True

        # When binary search finished, search in collection is still not
        # It is possible that more than one shape has point with specific X,
        # so collection could be like that, with search returned closest possible value:
        #
        # 0 5 7 10 10 10 13 20 25
        #           ^
        # Logic below handles this situation:
        # When detected result is greater or equal of what we search
        # shift index "to the left" until array ends or until result is lesser than searched value
        if self._nodeBoundaryPointsList[searchIndex][0].x() >= x:
            for boundaryIndex in reversed(range(0, searchIndex)):
                if self._nodeBoundaryPointsList[boundaryIndex][0].x() < x:
                    return boundaryIndex
            # Return 0 if x is least value among all
            return 0
        # Opposite case - shift index "to the right" until we find some value greater than searched one
        # As a result - this function returns index of the "first value on the left from searched one"
        # For x = 10 or x = 9 result will be [2] = 7
        #
        # 0 5 7 10 10 10 13 20 25
        #     ^
        else:
            for boundaryIndex in range(searchIndex, len(self._nodeBoundaryPointsList)):
                if self._nodeBoundaryPointsList[boundaryIndex][0].x() > x:
                    return boundaryIndex - 1
            # Or return last array's index
            return len(self._nodeBoundaryPointsList) - 1

    # Returns list of shapes, which boundary boxes intersect with specified point
    def __getBoundaryIntersectedShapesListAtPoint(self, point: QPoint) -> set[CustomShape]:
        searchStartIndex = self.__findClosestBoundaryPointIndex(point.x())

        possibleShapes = set()

        # Handle empty search result - return empty set
        if searchStartIndex < 0:
            return possibleShapes

        for i in range(searchStartIndex, len(self._nodeBoundaryPointsList)):
            # Point could be on shape if its Y falls between Y coords of shape's borders
            if self._nodeBoundaryPointsList[i][1].getTopLeftBound().y() <= point.y() and self._nodeBoundaryPointsList[i][1].getBottomRightBound().y() >= point.y():
                possibleShapes.add(self._nodeBoundaryPointsList[i][1])

        return possibleShapes

    # Clears collection and all related variables
    def clearCollection(self) -> None:
        self._shapesList.clear()
        self._nodeBoundaryPointsList.clear()
        self._shapeMaxWidth = 0

# Class to check for shapes collisions/overlaps
# Requires area to process borders collisions 
# and collection of shapes to process collisions between shapes
#
# Current implemetation is ineffective and uses simple iterating through entire shapes collection
# This works for a small number of shapes, but will lead to poor performance for bigger collection
class CollisionProcessor():
    def __init__(self, drawingWidget: QWidget, shapesCollection: ShapesCollection) -> None:
        self._drawingWidget = drawingWidget
        self._shapesCollection = shapesCollection

    # Check if new shape fits into draw area
    def areaBorderCheck(self, shape: CustomShape) -> bool:
        if shape.getTopLeftBound().x() < 0 or shape.getTopLeftBound().y() < 0:
            return False

        if shape.getBottomRightBound().x() > self._drawingWidget.width() or shape.getBottomRightBound().y() > self._drawingWidget.height():
            return False
        
        return True
    
    # Check collisions with other shapes
    def shapeCollisionCheck(self, shape: CustomShape) -> bool:
        # Get list of shapes with intersecting boundary boxes
        possibleIntersections = self._shapesCollection.getBoundaryIntersectedShapesSet(shape)

        # For this shapes check actual intersections
        for possibleIntersection in possibleIntersections:
            if possibleIntersection.checkIntersectionPrecise(shape):
                return False
            
        return True
    
    # Complete collision check
    def completeCollisionCheck(self, shape: CustomShape) -> bool:
        return self.areaBorderCheck(shape) and self.shapeCollisionCheck(shape)