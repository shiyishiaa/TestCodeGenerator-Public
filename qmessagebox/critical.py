from typing import Optional

from PySide6.QtWidgets import QWidget, QMessageBox

from .QMessageBoxFactory import MessageBoxFactory

__title__ = "Critical"


def failed_to_hallucinate(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[
    QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Failed to hallucinate!"
    return MessageBoxFactory.critical(parent, **kwargs)


def failed_to_generate(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[
    QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Failed to generate!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def failed_to_save(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Failed to save!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def invalid_configuration(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[
    QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Invalid configuration!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def invalid_file(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Invalid file!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def invalid_folder(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Invalid folder!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def invalid_provider(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Invalid provider!"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)


def unexpected_error(parent: QWidget, *, exception: Exception = None, **kwargs) -> Optional[QMessageBox.StandardButton]:
    if "title" not in kwargs:
        kwargs["title"] = __title__
    if "message" not in kwargs:
        kwargs["message"] = "Unexpected error"
    if "exception" not in kwargs and exception is not None:
        kwargs["exception"] = exception
    return MessageBoxFactory.critical(parent, **kwargs)
