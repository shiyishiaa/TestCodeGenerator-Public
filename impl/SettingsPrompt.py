from PySide6.QtCore import Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QWidget, QMessageBox, QDialogButtonBox

from constant import PROMPT_CODE, PROMPT_CONTENT
from qmessagebox import save_changes
from qwindow import SettingsPromptUi
from util import read_settings, write_settings

__PROMPT_CONTENT__ = None
__PROMPT_CODE__ = None


class SettingsPrompt(QDialog, SettingsPromptUi):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setupUi(self)

        self.__setup_ui_components()
        self.__connect_signals()

    def __setup_ui_components(self) -> None:
        """Setup UI components"""
        global __PROMPT_CONTENT__, __PROMPT_CODE__

        __PROMPT_CONTENT__ = read_settings('Prompt', 'content', default=PROMPT_CONTENT)
        __PROMPT_CODE__ = read_settings('Prompt', 'code', default=PROMPT_CODE)

        self.prompt_content.setPlainText(__PROMPT_CONTENT__)
        self.prompt_code.setPlainText(__PROMPT_CODE__)

    def __connect_signals(self) -> None:
        """Connect all signals and slots"""
        self.button_box.accepted.connect(self.on_button_box_accepted)
        self.button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self.on_restore_defaults_clicked)

    @Slot()
    def on_button_box_accepted(self) -> None:
        """Save settings"""
        write_settings('Prompt', 'content', self.prompt_content.toPlainText())
        write_settings('Prompt', 'code', self.prompt_code.toPlainText())

    @Slot()
    def on_restore_defaults_clicked(self) -> None:
        """Restore defaults"""
        self.prompt_content.setPlainText(PROMPT_CONTENT)
        self.prompt_code.setPlainText(PROMPT_CODE)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Close event"""
        edited = self.prompt_content.toPlainText() != __PROMPT_CONTENT__ or self.prompt_code.toPlainText() != __PROMPT_CODE__
        if edited and (reply := save_changes(self)):
            if QMessageBox.StandardButton.Yes == reply:
                self.on_button_box_accepted()
            elif QMessageBox.StandardButton.Cancel == reply:
                event.ignore()
                return
        event.accept()
