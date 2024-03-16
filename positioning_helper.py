import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

import constants
from custom_rect import CustomRect

class ShapeNode():
    def __init__(self, shape: CustomRect) -> None:
        self.shape = shape
        self.left: ShapeNode = None
        self.right: ShapeNode = None

    # TODO: This equality check is costly - it goes through all tree. Should think on optimization
    def __eq__(self, __value: object) -> bool:
        if type(__value) is ShapeNode:
            if self.shape == __value.shape and self.left == __value.left and self.right == __value.right:
                return True
            
        return False
    
class ShapeNodesCollection():
    def __init__(self) -> None:
        self._root: ShapeNode = None

    def addNode(self, shape: CustomRect) -> None:
        if self._root == None:
            self._root = ShapeNode(shape)
        else:
            self.__addNodeInternal(self._root, ShapeNode(shape), 0)

    def __addNodeInternal(self, root: ShapeNode, node: ShapeNode, depth: int) -> ShapeNode:
        if not root:
            return node

        currentDimension = depth % 2

        if (ShapeNodesCollection.getCoordsDimension(node.shape.centerPoint, currentDimension) < ShapeNodesCollection.getCoordsDimension(root.shape.centerPoint, currentDimension)):
            root.left = self.__addNodeInternal(root.left, node, depth + 1)
        else:
            root.right = self.__addNodeInternal(root.right, node, depth + 1)

        return root
    
    def searchNearestNode(self, point: QPoint) -> CustomRect:
        result = self.__searchNearestNodeInternal(self._root, point, 0)

        if result:
            return result.shape
        else:
            return None
    
    def __searchNearestNodeInternal(self, root: ShapeNode, point: QPoint, depth: int) -> ShapeNode:
        if not root:
            return None
            
        currentDimension = depth % 2

        if (ShapeNodesCollection.getCoordsDimension(point, currentDimension) < ShapeNodesCollection.getCoordsDimension(root.shape.centerPoint, currentDimension)):
            nextBranch = root.left
            otherBranch = root.right
        else:
            nextBranch = root.right
            otherBranch = root.left

        temp: ShapeNode = self.__searchNearestNodeInternal(nextBranch, point, depth + 1)
        best: ShapeNode = ShapeNodesCollection.__closestNode(point, temp, root)

        bestDist = ShapeNodesCollection.__calcDistance(best.shape.centerPoint, point)
        planeDist = abs(ShapeNodesCollection.getCoordsDimension(point, currentDimension) - ShapeNodesCollection.getCoordsDimension(root.shape.centerPoint, currentDimension))

        if bestDist >= planeDist:
            temp = self.__searchNearestNodeInternal(otherBranch, point, depth + 1)
            best = ShapeNodesCollection.__closestNode(point, temp, best)

        return best

    @staticmethod
    def getCoordsDimension(point: QPoint, dimension: int) -> int:
        if dimension == 0:
            return point.x()
        elif dimension == 1:
            return point.y()
        else:
            raise IndexError(f"Dimension {dimension} is not supported for 2D shapes")

    def getShapeAtPoint(self, point: QPoint) -> CustomRect:
        return self.__searchNode(ShapeNode(point))

    def __searchNode(self, root: ShapeNode, node: ShapeNode, depth: int) -> ShapeNode:
        if not root:
            return None
        
        if root.shape == node.shape:
            return root
        
        currentDepth = depth % 2

        if node.getCoordinateInDimension(currentDepth) < root.getCoordinateInDimension(currentDepth):
            return self.__searchNode(root.left, node, depth + 1)
        
        return self.__searchNode(root.right, node, depth + 1)

    @staticmethod
    def __closestNode(targetPoint: QPoint, node_1: ShapeNode, node_2: ShapeNode) -> ShapeNode:
        if not node_1:
            return node_2
        
        if not node_2:
            return node_1
        
        len1 = ShapeNodesCollection.__calcDistance(node_1.shape.centerPoint, targetPoint)
        len2 = ShapeNodesCollection.__calcDistance(node_2.shape.centerPoint, targetPoint)

        if len1 < len2:
            return node_1
        else:
            return node_2

    @staticmethod
    def __calcDistance(point_1: QPoint, point_2: QPoint) -> float:
        cat1 = point_1.x() - point_2.x()
        cat2 = point_1.y() - point_2.y()

        return (cat1**2 + cat2**2)**0.5