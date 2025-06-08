from enum import Enum
from typing import Optional, Callable

from PySide6.QtWidgets import QWidget, QMessageBox


class MessageType(str, Enum):
    CRITICAL = "critical"
    INFORMATION = "information"
    WARNING = "warning"
    QUESTION = "question"


class MessageBoxFactory:
    """
    Factory class to create standardized message boxes with consistent formatting
    and reduced code duplication.
    """

    @staticmethod
    def __create_message_box(
            parent: QWidget,
            msg_type: MessageType,
            title: str,
            message: str,
            buttons: QMessageBox.StandardButton,
            default_button: QMessageBox.StandardButton,
            exception: Exception = None,
            **kwargs
    ) -> Optional[QMessageBox.StandardButton]:
        """
        Internal method to create and show a message box with consistent formatting.

        Args:
            parent: Parent widget
            msg_type: Type of message box
            title: Title of the message box
            message: Main message content
            buttons: Buttons to display
            default_button: Default selected button
            exception: Optional exception to display
            **kwargs: Additional key-value pairs to display

        Returns:
            The clicked button
        """
        # Append exception if provided
        if exception:
            message += f"\n{exception}"

        # Append additional information
        for key, value in kwargs.items():
            message += f"\n{key}: {value}"

        # Use the appropriate QMessageBox method based on a message type
        message_func: Callable = getattr(QMessageBox, msg_type.value)

        return message_func(
            parent,
            title,
            message,
            default_button,
            buttons
        )

    @classmethod
    def critical(
            cls,
            parent: QWidget,
            *,
            title: str = "Critical",
            message: str,
            exception: Exception = None,
            **kwargs
    ) -> Optional[QMessageBox.StandardButton]:
        """Shows a critical message box."""
        return cls.__create_message_box(
            parent,
            MessageType.CRITICAL,
            title,
            message,
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.NoButton,
            exception,
            **kwargs
        )

    @classmethod
    def warning(
            cls,
            parent: QWidget,
            *,
            title: str = "Warning",
            message: str,
            yes_no: bool = False,
            exception: Exception = None,
            **kwargs
    ) -> Optional[QMessageBox.StandardButton]:
        """Shows a warning message box."""
        buttons = QMessageBox.StandardButton.Cancel if yes_no else QMessageBox.StandardButton.NoButton
        default_button = QMessageBox.StandardButton.Ok

        return cls.__create_message_box(
            parent,
            MessageType.WARNING,
            title,
            message,
            buttons,
            default_button,
            exception,
            **kwargs
        )

    @classmethod
    def information(
            cls,
            parent: QWidget,
            *,
            title: str = "Information",
            message: str,
            exception: Exception = None,
            **kwargs
    ) -> Optional[QMessageBox.StandardButton]:
        """Shows an information message box."""
        return cls.__create_message_box(
            parent,
            MessageType.INFORMATION,
            title,
            message,
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.NoButton,
            exception,
            **kwargs
        )

    @classmethod
    def question(
            cls,
            parent: QWidget,
            *,
            title: str = "Question",
            message: str,
            exception: Exception = None,
            **kwargs
    ) -> Optional[QMessageBox.StandardButton]:
        """Shows a question message box with Yes, No, and Cancel buttons."""
        buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel

        return cls.__create_message_box(
            parent,
            MessageType.QUESTION,
            title,
            message,
            QMessageBox.StandardButton.NoButton,
            buttons,
            exception,
            **kwargs
        )
