from typing import Optional

from PySide6.QtWidgets import QWidget, QMessageBox

from .QMessageBoxFactory import MessageBoxFactory

__title__ = "Information"


def task_completed(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Task completed!"
    return MessageBoxFactory.information(parent, **kwargs)
