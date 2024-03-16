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

    def getCoordinateInDimension(self, dimension: int) -> int:
        if dimension == 0:
            return self.shape.centerPoint.x()
        elif dimension == 1:
            return self.shape.centerPoint.y()
        else:
            raise IndexError(f"Dimension {dimension} is not supported for 2D shapes")
        
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

        if (node.getCoordinateInDimension(currentDimension) < root.getCoordinateInDimension(currentDimension)):
            root.left = self.__addNodeInternal(root.left, node, depth + 1)
        else:
            root.right = self.__addNodeInternal(root.right, node, depth + 1)

        return root
    
    def searchNearestNode(self, shape: CustomRect) -> CustomRect:
        result = self.__searchNearestNodeInternal(self._root, ShapeNode(shape), 0)

        if result:
            return result.shape
        else:
            return None
    
    def __searchNearestNodeInternal(self, root: ShapeNode, node: ShapeNode, depth) -> ShapeNode:
        if not root:
            return None
            
        currentDimension = depth % 2

        if (node.getCoordinateInDimension(currentDimension) < root.getCoordinateInDimension(currentDimension)):
            nextBranch = root.left
            otherBranch = root.right
        else:
            nextBranch = root.right
            otherBranch = root.left

        temp: ShapeNode = self.__searchNearestNodeInternal(nextBranch, node, depth + 1)
        best: ShapeNode = ShapeNodesCollection.__closestPoint(node, temp, root)

        bestDist = ShapeNodesCollection.__calcDistance(best, node)
        planeDist = abs(node.getCoordinateInDimension(currentDimension) - root.getCoordinateInDimension(currentDimension))

        if bestDist >= planeDist:
            temp = self.__searchNearestNodeInternal(otherBranch, node, depth + 1)
            best = ShapeNodesCollection.__closestPoint(node, temp, best)

        return best

    @staticmethod
    def __closestPoint(target: ShapeNode, node_1: ShapeNode, node_2: ShapeNode) -> ShapeNode:
        if not node_1:
            return node_2
        
        if not node_2:
            return node_1
        
        len1 = ShapeNodesCollection.__calcDistance(node_1, target)
        len2 = ShapeNodesCollection.__calcDistance(node_2, target)

        if len1 < len2:
            return node_1
        else:
            return node_2

    @staticmethod
    def __calcDistance(node_1: ShapeNode, node_2: ShapeNode) -> float:
        cat1 = node_1.getCoordinateInDimension(0) - node_2.getCoordinateInDimension(0)
        cat2 = node_1.getCoordinateInDimension(1) - node_2.getCoordinateInDimension(1)

        return (cat1**2 + cat2**2)**0.5