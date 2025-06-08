from contextlib import contextmanager
from typing import Any, Iterator, Type, TypeVar

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget
from loguru import logger

from constant import ORGANIZATION, APPLICATION
from entity import ModelSettings, __GROUP_PROPERTY__
from .util_common import decrypt, encrypt

T = TypeVar('T')


@contextmanager
def block_signals(*widgets: QWidget):
    # Store original blocking states for all widgets
    original_states = [(widget, widget.signalsBlocked()) for widget in widgets]

    try:
        # Block signals for all specified widgets
        for widget in widgets:
            widget.blockSignals(True)
        yield
    finally:
        # Restore original blocking states
        for widget, was_blocked in original_states:
            widget.blockSignals(was_blocked)


@contextmanager
def sync_settings(group: str) -> Iterator[QSettings]:
    """Sync settings"""
    settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ORGANIZATION, APPLICATION)
    settings.beginGroup(group)
    try:
        yield settings
    finally:
        settings.endGroup()
        settings.sync()


# noinspection PyBroadException
def read_settings(group: str, key: str, /, default: Any = None, type_: Type[T] = str) -> T:
    """
    Read the settings and ensure no exception is raised.

    Args:
        group: The group of the settings
        key: The key of the settings
        default: The default value if the key is not found
        type_: The type of the value

    Returns:
        The value of the settings.
        If the key is not found, the default value is returned.
        If no default value is provided, the type of the value is returned.
    """
    with sync_settings(group) as settings:
        try:
            if type_:
                return type_(settings.value(key, default))
            else:
                return settings.value(key, default)
        except Exception:
            return type_() if default is None else default


def write_settings(group: str, key: str, value: Any, /) -> None:
    """
    Write settings.

    Args:
        group: The group of the settings
        key: The key of the settings
        value: The value to write
    """
    with sync_settings(group) as settings:
        settings.setValue(key, value)


# noinspection PyBroadException
def read_model_settings() -> ModelSettings:
    """
    Read the model settings.
    """

    config_data = {}
    for name, field_info in ModelSettings.__pydantic_fields__.items():
        group = field_info.json_schema_extra.get(__GROUP_PROPERTY__)

        value = read_settings(group, name, field_info.default)
        if "api_key" in name:
            try:
                value = decrypt(value)
            except Exception:
                logger.error("Error decrypting api key!")
        config_data[name] = value

    return ModelSettings(**config_data)


def write_model_settings(model_settings: ModelSettings) -> None:
    """
    Write the model settings.
    """

    for name, field_info in model_settings.model_fields.items():
        group = field_info.json_schema_extra.get(__GROUP_PROPERTY__)

        value = getattr(model_settings, name)
        if "api_key" in name:
            value = encrypt(value)

        write_settings(group, name, value)
