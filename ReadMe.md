**DESCRIPTION**

The program uses Python 3.12.2 and PyQt5 to implement simple shape draw with specific behavior

**FUNCTIONS GUIDE**
- Create rectangle with random color, fixed default size: 
    - LMB double-click
    - Toolbar -> Create rect -> LMB click at desired point.
- Move shape:
    - Drag and drop shape with LMB
    - Toolbar -> Move shape -> LMB lick on shape to move -> LMB click on new position
- Create line between shapes:
    - MMB click on first shape, then MMB click on second shape
    - Toolbar -> Create link -> LMB click on first shape -> LMB click on second shape
- Cancel current action:
    - RMB click
- Delete shape:
    - Double-click with RMB on shape
- Clear drawing area:
    - Toolbar -> Clear area

**CONSTANTS GUIDE**

Constans are located at [constants.py](constants.py) file. Here is short description of them, with some constants grouped by purpose:
- `MAIN_WINDOW_START_POSITION` - coordinates of start position for the window
- `MAIN_WINDOW_SIZE` - size of program's window, this size is fixed
- `RECT_SIZE` - default size for rectangle shape in pixels
- `RECT_DEFAULT_COLOR` - default color for rectangle shape

Also this file contains texts for menu buttons for simplicity. However, usually such data is located in separate localization resource files.

**POSITIONING HELPERS EXPLANATION**

This project contains 3 positioning helper implementation. Here is short breakdown on what they are.

***[positioning_helper.py](positioning_helper.py)***

First implemetation of effective collection to store data about shapes positions and search for intersections and shapes at specific points. Idea was to find closest shape to specified point, using K-D tree, then check, if it intersects with specified point or specified shape. Unfortunately, this didn't work for purposes of this program, and rework seemed too complicated, so second implementation was used.


***[positioning_helper_ineffective.py](positioning_helper_ineffective.py)***

Workaround helper, which used straight-forward search through entire collection of shapes to check, if there are any intersections with specified shape/point. This solution wouldn't work good enough for big number of shapes in draw area, but was good enough for development purposes and allowed to finish main functionality in time. However, some room has been left to replace it with more effective search in future.

***[positioning_helper_v2.py](positioning_helper_v2.py)***

New implementation for same goal: fast and effective search for shapes at specified coordinates and shapes intersecting with specified shape. Idea behind this is following: if we have number of non-intersectin shapes on a plane, and we know properties of bounding rectangle (bounding box) of each of these shapes, we can quickly determine, if specified shape's bounding box intersects with any of bounding boxes of shapes in collection. Steps are following:
- Upon addition of shape to collection, store its bounding box's top-lef and bottom-right corners coordinates to metadata list, sorted by X coordinate. Along with point data store link to it's shape.
- Also upon addition check and store widest shape width.
- Upon search for intersections with **shape A**:
  - Using binary search find in metadata list point, which X coordinate is equal or slightly less, than X coordinate of top-left corner of bounding box of **shape A**
  - Iterate through metadata list until delta between **shape A** top-left X and X of stored point exceeds widest shape's width
  - Upon iteration save any shapes, for which Y coordinate of **shape A** corner point falls between Y coodinates of top and bottom bounds - these are the shapes, which bounding boxes intersect bounding box of **shape A**
  - Repeat search for bottom-left corner of **shape A**
  - Return set of shapes, found during two previous searches.

In other words, instead of checking intersections with each shape on plane, perform check - if top or bottom sections of **shape A** intersect with any shape's bounds in range of X between start and end of those sections.

Comparing with `positioning_helper_ineffective`:
- Insertion is O(log n) vs O(1) - worse
- Search is O(log n) vs O(n) - better
- Deletion is O(log n) vs O(n) - better

However, there is worst-case scenario, when all shapes have same X of top-left and same X of bottom-right corners (shapes stacked vertically on each other), and in this case new `positioning_helper_v2` will perform even worse than `positioning_helper_ineffective`