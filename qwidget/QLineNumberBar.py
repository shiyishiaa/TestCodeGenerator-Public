from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget


class QLineNumberBar(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.adjust_width()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(240, 240, 240))

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.GlobalColor.darkGray)
                painter.drawText(
                    0, int(top), self.width(), self.editor.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight, number
                )

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

    def adjust_width(self):
        digits = len(str(max(1, self.editor.blockCount())))
        space = 20 + self.editor.fontMetrics().horizontalAdvance('9') * digits
        self.setFixedWidth(space)
