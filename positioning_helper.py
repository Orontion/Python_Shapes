import sys

from typing import Union, List

from PyQt5 import QtWidgets
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QBrush, QPen, QPalette, QColor
from PyQt5.QtCore import Qt, QRect, QSize, QPoint

from custom_rect import CustomRect

# First iteration of shapes positioning classes
# Work abandoned as this solution did not provide expected result
# and rework would cost too much of time


# Class for K-D Tree implemetation
class ShapeNode():
    def __init__(self, shape: CustomRect) -> None:
        self.shape = shape
        self.dimension: int = 0
        self.left: ShapeNode = None
        self.right: ShapeNode = None
        self.parent: ShapeNode = None

    # TODO: This equality check is costly - it goes through all tree. Should think on optimization
    def __eq__(self, __value: object) -> bool:
        if type(__value) is ShapeNode:
            if self.shape == __value.shape and self.left == __value.left and self.right == __value.right:
                return True
            
        return False
    
# Shapes collection based on K-D Tree for effective search
class ShapeNodesCollection():
    def __init__(self) -> None:
        self._root: ShapeNode = None

    # Root element
    @property
    def root(self) -> ShapeNode:
        return self._root

    # Public method to add shape
    def addShape(self, shape: CustomRect, dimensionStart: int = 0) -> None:
        if self._root == None:
            self._root = ShapeNode(shape)
        else:
            self.__addNodeInternal(self._root, ShapeNode(shape), dimensionStart)

    # Internal recursion based method to add shape to tree
    def __addNodeInternal(self, root: ShapeNode, node: ShapeNode, depth: int) -> None:

        currentDimension = depth % 2

        if (ShapeNodesCollection.getCoordsDimension(node.shape.centerPoint, currentDimension) < ShapeNodesCollection.getCoordsDimension(root.shape.centerPoint, currentDimension)):
            if not root.left:
                node.parent = root
                node.dimension = (depth + 1) % 2
                root.left = node
                return
            else:
                self.__addNodeInternal(root.left, node, depth + 1)
        else:
            if not root.right:
                node.parent = root
                node.dimension = (depth + 1) % 2
                root.right = node
                return
            else:
                root.right = self.__addNodeInternal(root.right, node, depth + 1)

        return root
    
    # Public method for searching shape closest to specified point
    def searchNearestShape(self, point: QPoint) -> CustomRect:
        result = self.__searchNearestNodeInternal(self._root, point, 0)

        if result:
            return result.shape
        else:
            return None
    
    # Internal recursion based search through K-D Tree
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

    # Static method to simplify code and switch metween X and Y using index
    # Should be internal
    @staticmethod
    def getCoordsDimension(point: QPoint, dimension: int) -> int:
        if dimension == 0:
            return point.x()
        elif dimension == 1:
            return point.y()
        else:
            raise IndexError(f"Dimension {dimension} is not supported for 2D shapes")

    # Public method to get a shape at certain point (collection assumes shapes can't intersect)
    def getShapeAtPoint(self, point: QPoint) -> CustomRect:
        return self.__searchNode(ShapeNode(point))

    # Public method for shape deletion
    def deleteShape(self, shape: CustomRect) -> None:
        nodeToDelete = self.__searchNode(self._root, ShapeNode(shape), 0)

        if nodeToDelete:
            print(f"Found node: {nodeToDelete.shape.centerPoint.x()}, {nodeToDelete.shape.centerPoint.y()}")
            # self.__deleteNodeInternal(nodeToDelete.parent, nodeToDelete)
        else:
            print("No nodes found")

    # Internal recursive method for shape search
    def __searchNode(self, root: ShapeNode, node: ShapeNode, depth: int) -> ShapeNode:
        if not root:
            return None
        
        if root.shape == node.shape:
            return root
        
        currentDimension = depth % 2

        if ShapeNodesCollection.getCoordsDimension(node.shape.centerPoint, currentDimension) < ShapeNodesCollection.getCoordsDimension(root.shape.centerPoint, currentDimension):
            return self.__searchNode(root.left, node, depth + 1)
        
        return self.__searchNode(root.right, node, depth + 1)

    # Internal method for deletion shape from collection
    # NOT FINISHED
    def __deleteNodeInternal(self, root: ShapeNode, node: ShapeNode) -> None:
        print("Starting deletion")
        startingDim = root.dimension

        subnodesList = []

        print(f"Node left: {node.left}")
        print(f"Node right: {node.right}")

        # self.__addNodeToList(node.left, subnodesList)
        # self.__addNodeToList(node.right, subnodesList)

        print(f"Subnodes collection size: {len(subnodesList)}")

        newCollection = ShapeNodesCollection()

        for node in subnodesList:
            newCollection.addShape(node.shape, startingDim)

        print(f"Deleted node dim: {node.dimension}")
        print(f"New subtree start dim: {newCollection.root.dimension}")

    # This method was supposed to store shapes to list for ease of access
    # NOT FINISHED
    def __addNodeToList(self, node: ShapeNode, nodeList: List[ShapeNode]) -> None:
        if not node:
            return

        if node.left:
            self.__addNodeToList(node.left, nodeList)
        
        if node.right:
            self.__addNodeToList(node.right, nodeList)

        nodeList.append(node)

    # Internal static method for closest shape selection based on center point
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

    # Internal static method to calculate distance between points
    @staticmethod
    def __calcDistance(point_1: QPoint, point_2: QPoint) -> float:
        cat1 = point_1.x() - point_2.x()
        cat2 = point_1.y() - point_2.y()

        return (cat1**2 + cat2**2)**0.5