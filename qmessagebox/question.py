from typing import Optional

from PySide6.QtWidgets import QWidget, QMessageBox

from qmessagebox.QMessageBoxFactory import MessageBoxFactory

__title__ = "Question"


def save_changes(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Save changes?"
    return MessageBoxFactory.question(parent, **kwargs)
