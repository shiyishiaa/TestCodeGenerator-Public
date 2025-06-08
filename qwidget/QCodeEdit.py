from typing import Type

from PySide6.QtCore import QRect
from PySide6.QtGui import QFont, QSyntaxHighlighter
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from qobject import QJavaScriptHighlighter
from .QLineNumberBar import QLineNumberBar


class QCodeEdit(QPlainTextEdit):

    def __init__(self,
                 code: str = "",
                 /,
                 parent: QWidget = None,
                 *,
                 syntax_highlighter: Type[QSyntaxHighlighter] = QJavaScriptHighlighter, ):
        super().__init__(parent)
        self.line_number_bar = QLineNumberBar(self)
        self.setViewportMargins(self.line_number_bar.width(), 0, 0, 0)
        self.setFont(QFont("Consolas", 12))
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

        self.setPlainText(code)
        syntax_highlighter(self.document())

        # Connect signals
        self.blockCountChanged.connect(self.update_line_number_width)
        self.updateRequest.connect(self.update_line_numbers)
        self.textChanged.connect(self.update_line_numbers)

    def update_line_number_width(self):
        self.line_number_bar.adjust_width()
        self.setViewportMargins(self.line_number_bar.width(), 0, 0, 0)

    def update_line_numbers(self):
        self.line_number_bar.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_bar.setGeometry(QRect(cr.left(), cr.top(), self.line_number_bar.width(), cr.height()))
