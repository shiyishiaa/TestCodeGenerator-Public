import os
from typing import Union

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPixmap, QWheelEvent, QPainter, QMouseEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem


class QImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize scene and set it to the view
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Keep track of the image pixmap item and zoom scale factor
        self._pixmap_item = None
        self._zoom = 0

        # Set up default settings for the view
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Flag to track if the mouse is being pressed and moved for panning
        self._panning = False
        self._last_pan_point = QPointF()

    def load_image(self, path: Union[str, bytes, os.PathLike]):
        """
        Load an image from the given file path and display it.
        """
        # Clear any previously loaded image
        if self._pixmap_item:
            self.scene.removeItem(self._pixmap_item)
            self._pixmap_item = None

        # Load the new image
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            # Create a QGraphicsPixmapItem and scale it to fit the view initially
            self._pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self._pixmap_item)
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.centerOn(self._pixmap_item)  # Center the image in the view

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Override wheelEvent to handle zooming in/out when Ctrl key is pressed.
        """
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Calculate the zoom delta based on the wheel event
            zoom_in = event.angleDelta().y() > 0
            zoom_factor = 1.25 if zoom_in else 1 / 1.25

            # Save the current view center point
            old_center = self.mapToScene(event.position().toPoint())

            # Apply the zoom
            self.scale(zoom_factor, zoom_factor)

            # Adjust the view to keep the same center point after zooming
            new_center = self.mapToScene(event.position().toPoint())
            delta = old_center - new_center
            self.translate(delta.x(), delta.y())

            # Accept the event to prevent further propagation
            event.accept()
        else:
            # If Ctrl is not pressed, pass the event to the base class
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Override mousePressEvent to start panning when left button is pressed.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_pan_point = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Override mouseMoveEvent to handle panning.
        """
        if event.buttons() == Qt.MouseButton.LeftButton and self._panning:
            # Calculate the pan delta and move the scene
            delta = event.position().toPoint() - self._last_pan_point
            self._last_pan_point = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()  # Accept the event to prevent default handling
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.buttons() == Qt.MouseButton.LeftButton:
            # Horizontal movement when Shift is pressed
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - (event.position().toPoint() - self._last_pan_point).x())
            self._last_pan_point = event.position().toPoint()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Override mouseReleaseEvent to stop panning when left button is released.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = False
        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """
        Override resizeEvent to ensure the image stays centered when the view is resized.
        """
        if self._pixmap_item:
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.centerOn(self._pixmap_item)  # Center the image in the view
        super().resizeEvent(event)
