from typing import Optional

from PySide6.QtWidgets import QWidget, QMessageBox

from .QMessageBoxFactory import MessageBoxFactory

__title__ = "Warning"


def too_few_files(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Too few files!"
    return MessageBoxFactory.warning(parent, **kwargs)


def too_many_files(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Too many files!"
    return MessageBoxFactory.warning(parent, **kwargs)


def leave_while_running(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Leave while running?"
    if "yes_no" not in kwargs:
        kwargs["yes_no"] = True
    return MessageBoxFactory.warning(parent, **kwargs)


def leave_without_saving(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Leave without saving?"
    if "yes_no" not in kwargs:
        kwargs["yes_no"] = True
    return MessageBoxFactory.warning(parent, **kwargs)


def overwrite_files(parent: QWidget, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Overwrite files?"
    if "yes_no" not in kwargs:
        kwargs["yes_no"] = True
    return MessageBoxFactory.warning(parent, **kwargs)
