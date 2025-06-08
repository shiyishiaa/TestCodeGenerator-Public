import os
from pathlib import Path
from typing import Optional, Union

from PySide6.QtCore import Signal, Slot, QThread, QThreadPool
from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QTextEdit, QPushButton, QMessageBox, QPlainTextEdit, \
    QFormLayout, QHBoxLayout, QFileDialog, QLayout, QCheckBox
from binaryornot import check
from loguru import logger

import constant
from entity import Detail, CodeBlock
from qmessagebox import failed_to_generate, invalid_file, invalid_folder, overwrite_files, task_completed
from qobject import QSimpleChatWorker, QPythonHighlighter, QTypeScriptHighlighter, QJavaScriptHighlighter
from util import block_signals, extract_code_blocks, read_settings, write_settings
from .QCodeEdit import QCodeEdit
from .QPager import QPager


# noinspection PyBroadException
def can_access(path: Union[str, Path]) -> bool:
    """
    Check if the path exists and is accessible.

    Args:
        path: The path to check.

    Returns:
        True if the path exists and is accessible, False otherwise.
    """
    path = Path(path)
    if path.exists() and path.is_dir() and os.access(path, os.X_OK):
        try:
            path.iterdir()
            return True
        except Exception:
            return False
    return False


def is_text_file(path: Union[str, Path]) -> bool:
    """Check if the path is a text file.

    Args:
        path: The path to check.
    """
    return not check.is_binary(str(path))


def _get_initial_directory(
        file_location: Optional[str] = None,
        project_folder: Optional[str] = None
) -> Optional[str]:
    """Get the initial directory for file dialog based on saved settings.

    Args:
        file_location: Last selected file location
        project_folder: Last selected project folder

    Returns:
        Initial directory path or None if no valid path found
    """
    # Try last file location first
    if file_location and (file_folder := Path(file_location).parent):
        if can_access(file_folder):
            return str(file_folder.resolve())

    # Fallback to last project folder
    if project_folder and can_access(project_folder):
        return str(Path(project_folder).resolve())

    return None


def _calculate_relative_path(selected_file: str, project_path: str) -> Optional[str]:
    """Calculate the relative path from project root to the selected file.

    Args:
        selected_file: Absolute path of selected file
        project_path: Absolute path of project root

    Returns:
        Relative path or None if calculation fails
    """
    try:
        file_path = Path(selected_file).resolve()
        project_path = Path(project_path).resolve()

        if not str(file_path).startswith(str(project_path)):
            logger.error(f"Selected file {selected_file} is outside project directory")
            return None

        return str(file_path.relative_to(project_path)).replace("\\", "/").strip("/")
    except Exception as e:
        logger.error(f"Error calculating the relative path: {e}")
        return None


class QDetailWidget(QWidget):
    detailLoaded = Signal(Detail)
    detailEdited = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._detail = None
        self._image = None

        self.form_layout = QFormLayout(self)
        self.__setup_ui_components()
        self.__connect_signals()

    def __setup_ui_components(self):
        # Project Folder
        self.project = QLineEdit(self)
        self.project.setReadOnly(True)
        self.project.setPlaceholderText("Project Folder")
        self.project_button = QPushButton("...")

        self.project_area = QHBoxLayout()
        self.project_area.addWidget(self.project)
        self.project_area.addWidget(self.project_button)
        self.add_pair("Project Folder", self.project_area)

        # File Location
        self.upload_code = QCheckBox("Upload Code", self)
        self.upload_code.setChecked(read_settings("upload_code", "upload_code", default=True, type_=bool))
        self.upload_code.setToolTip("Upload the code to AI")
        self.upload_code.setToolTipDuration(3000)
        self.upload_code.setDisabled(True)

        self.location = QLineEdit(self)
        self.location.setPlaceholderText("src/App.vue (Select project folder to enable the file location button)")
        self.location_button = QPushButton("...")
        self.location_button.setToolTip("Select project folder first")
        self.location_button.setToolTipDuration(3000)

        self.location_area = QHBoxLayout()
        self.location_area.addWidget(self.location)
        self.location_area.addWidget(self.upload_code)
        self.location_area.addWidget(self.location_button)
        self.add_pair("File Location", self.location_area)

        # Framework
        self.framework = QComboBox(self)
        self.framework.setEditable(True)
        self.framework.lineEdit().setPlaceholderText("Select framework")
        self.framework.addItems(
            ["Vue.js 2", "Vue.js 3", "React", "Angular", "jQuery", "Svelte", "Next.js", "Nuxt.js", ])
        self.framework.setCurrentIndex(-1)
        self.add_pair("Framework", self.framework)

        # Code Language
        self.language = QComboBox(self)
        self.language.setEditable(True)
        self.language.lineEdit().setPlaceholderText("Select language")
        self.language.addItems(["JavaScript", "TypeScript", "Python"])
        self.framework.setCurrentIndex(-1)
        self.add_pair("Code Language", self.language)

        # Test Tool
        self.tool = QComboBox(self)
        self.tool.setEditable(True)
        self.tool.lineEdit().setPlaceholderText("Select tool")
        self.tool.addItems(
            ["Jest", "Cypress", "Playwright", "Puppeteer", "Selenium", "TestCafe", ])
        self.tool.setCurrentIndex(-1)
        self.add_pair("Test Tool", self.tool)

        # Image Content
        self.content = QPlainTextEdit(self)
        self.content.setPlaceholderText("This webpage depicts...")
        self.content.setFont(QFont('Consolas', 12))
        self.generate_content = QPushButton("Generate Content (Ctrl+Alt+C)")
        self.add_pair("Image Content", self.generate_content)
        self.add_single(self.content)

        # Code
        self.generate_code = QPushButton("Generate Code (Ctrl+Alt+X)", self)
        self.add_pair("Code", self.generate_code)

        self.code_pager = QPager(parent=self)
        self.add_single(self.code_pager)

        # Disable buttons when no image is selected
        self.generate_content.setEnabled(False)
        self.generate_code.setEnabled(False)

        # Workers and Threads
        self.content_worker = QSimpleChatWorker()
        self.content_worker.setAutoDelete(False)

        self.code_worker = QSimpleChatWorker()
        self.code_worker.setAutoDelete(False)

        self.code_no_desc_worker = QSimpleChatWorker()
        self.code_no_desc_worker.setAutoDelete(False)

        self.worker_thread_pool = QThreadPool(self)
        self.worker_thread_pool.setMaxThreadCount(QThread.idealThreadCount() * 2)

        # Shortcuts
        self.generate_content_shortcut = QShortcut(QKeySequence("Ctrl+Alt+C"), self.window())
        self.generate_code_shortcut = QShortcut(QKeySequence("Ctrl+Alt+X"), self.window())

    # noinspection DuplicatedCode
    def __connect_signals(self):
        # Detail fields
        self.project.textChanged.connect(lambda: self.can_upload_code())
        self.project.textChanged.connect(lambda: self.location_button.setEnabled(True))
        self.project_button.clicked.connect(lambda: self.open_project_folder_dialog())

        self.location.textChanged.connect(lambda: self.can_upload_code())
        self.location.textChanged.connect(lambda: self.detailEdited.emit(True))
        self.location_button.clicked.connect(lambda: self.open_file_location_dialog())

        self.upload_code.stateChanged.connect(self.on_upload_code_changed)

        self.framework.editTextChanged.connect(lambda: self.detailEdited.emit(True))
        self.language.editTextChanged.connect(lambda: self.detailEdited.emit(True))
        self.tool.editTextChanged.connect(lambda: self.detailEdited.emit(True))
        self.content.textChanged.connect(lambda: self.detailEdited.emit(True))

        # Workers
        self.content_worker.signals.finished.connect(self.on_content_worker_finished)
        self.content_worker.signals.failed.connect(self.on_worker_failed)

        self.code_worker.signals.finished.connect(self.on_code_worker_finished)
        self.code_worker.signals.failed.connect(self.on_worker_failed)

        # Generate buttons
        self.generate_content.clicked.connect(self.generate_content_clicked)
        self.generate_code.clicked.connect(self.generate_code_clicked)

        # Signals
        self.detailLoaded.connect(self.on_detail_loaded)

        # Shortcuts
        self.generate_content_shortcut.activated.connect(lambda: self.generate_content_clicked(True))
        self.generate_code_shortcut.activated.connect(lambda: self.generate_code_clicked(True))

    def add_single(self, item: Union[QWidget, QLayout]) -> None:
        """Add a single item to the form layout.

        Args:
            item: The item to add to the form layout.
        """
        self.form_layout.addRow(item)

    def add_pair(self, title: str, item: Union[QWidget, QLayout]) -> None:
        """Add a pair of title and item to the form layout.

        Args:
            title: The title of the item.
            item: The item to add to the form layout.
        """
        self.form_layout.addRow(title, item)

    @property
    def detail(self) -> Optional[Detail]:
        return self._detail

    @detail.setter
    def detail(self, detail: Detail) -> None:
        self._detail = detail
        self.detailLoaded.emit(detail)

    @property
    def image(self) -> Optional[str]:
        return self._image

    @image.setter
    def image(self, image_url: str) -> None:
        self._image = image_url

    @Slot()
    def open_project_folder_dialog(self):
        group = "Folder"
        key = "last_project_folder"
        caption = "Select Project Folder"

        path = Path(read_settings(group, key, default="", type_=str))
        if can_access(path):
            file_dialog = QFileDialog(self, caption, str(path.resolve()))
        else:
            file_dialog = QFileDialog(self, caption)

        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_folder = file_dialog.selectedFiles()[0]
            if can_access(selected_folder):
                self.project.setText(selected_folder)
                write_settings(group, key, selected_folder)
            else:
                invalid_folder(self, message="Invalid project folder!")

    @Slot()
    def open_file_location_dialog(self):
        # Load settings
        group = "Folder"
        key_project = "last_project_folder"
        key_location = "last_file_location"
        caption = "Select Source Code File"

        last_project_folder = read_settings(group, key_project, default="", type_=str)
        last_file_location = read_settings(group, key_location, default="", type_=str)

        # Get initial directory
        initial_dir = _get_initial_directory(last_file_location, last_project_folder)

        # Configure and show dialog
        file_dialog = QFileDialog(self, caption, initial_dir)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Source Code File (*.*)")

        if file_dialog.exec() != QFileDialog.DialogCode.Accepted:
            return

        selected_file = file_dialog.selectedFiles()[0]
        selected_file_path = Path(selected_file)
        if not all([selected_file_path.exists(), selected_file_path.is_file(), is_text_file(selected_file_path)]):
            invalid_file(self, message="Invalid source code file!")
            return

        # Calculate the relative path if the project is selected
        relative_path = _calculate_relative_path(selected_file, self.project.text())
        if not relative_path:
            invalid_file(self, message="Selected file is outside project directory!")
            return

        # Update UI and save settings
        self.location.setText(relative_path)
        write_settings(group, key_location, selected_file)

    @Slot()
    def can_upload_code(self):
        """
        Check if the upload code can be enabled.
        """
        if self.project.text() and self.location.text():
            source_code = Path(self.project.text()) / Path(self.location.text())
            if source_code.exists() and source_code.is_file():
                self.upload_code.setEnabled(True)
                return
        self.upload_code.setDisabled(True)

    @Slot(bool)
    def on_upload_code_changed(self, checked: bool):
        """
        Write the upload code setting to the settings file.
        """
        write_settings("upload_code", "upload_code", checked)

    @Slot(bool)
    def generate_content_clicked(self, _: bool):
        if self.content.toPlainText() and QMessageBox.StandardButton.Cancel == \
                overwrite_files(self, message="This action will clear the content field!"):
            return

        self.window().setDisabled(True)

        self.content_worker.system = read_settings('Prompt', 'content', default=constant.PROMPT_CONTENT)
        self.content_worker.text = None
        self.content_worker.image = self.image

        logger.info(f"Generating content for {self.content_worker.image}.")
        self.worker_thread_pool.start(self.content_worker)

    @Slot(str)
    def on_content_worker_finished(self, result: str):
        self.content.setPlainText(result)
        task_completed(self)
        self.window().setEnabled(True)

    @Slot(bool)
    def generate_code_clicked(self, _: bool):
        if self.code_pager.count() != 0 and QMessageBox.StandardButton.Cancel == \
                overwrite_files(self, message="This action will clear the code field!"):
            return

        self.window().setDisabled(True)

        self.code_worker.system = read_settings('Prompt', 'code', default=constant.PROMPT_CODE)
        self.code_worker.text = self.str_detail()
        self.code_worker.image = self.image

        logger.info(
            f"Generating code for {self.code_worker.image}. Prompt: {self.code_worker.system + self.code_worker.text}")
        self.worker_thread_pool.start(self.code_worker)

    @Slot(str)
    def on_code_worker_finished(self, result: str):
        self.code_pager.clear_pages()
        if codes := extract_code_blocks(result.strip()):
            for code_block in codes:
                code, language = code_block.code, code_block.language
                match language.lower():
                    case "python":
                        self.code_pager.add_page(
                            QCodeEdit(code, self, syntax_highlighter=QPythonHighlighter), language)
                    case "typescript" | "ts":
                        self.code_pager.add_page(
                            QCodeEdit(code, self, syntax_highlighter=QTypeScriptHighlighter), language)
                    case "javascript" | "js" | _:
                        self.code_pager.add_page(
                            QCodeEdit(code, self, syntax_highlighter=QJavaScriptHighlighter), language)
        else:
            self.code_pager.add_page(QTextEdit(result), "text")
        task_completed(self)
        self.window().setEnabled(True)

    @Slot(Exception)
    def on_worker_failed(self, error: Exception):
        failed_to_generate(self, exception=error)
        self.window().setEnabled(True)

    @Slot(Detail)
    def on_detail_loaded(self, detail: Detail):
        with block_signals(self.location, self.framework, self.language, self.tool, self.content):
            # Change
            self.content.setPlainText(detail.content)

            # Remain unchanged
            if project := detail.project:
                self.project.setText(project)

            if location := detail.location:
                self.location.setText(location)
                self.location.setStyleSheet("")
            else:
                # Notify user that the location is not changed
                self.location.setStyleSheet("QLineEdit { color: red; font-weight: bold; }")

            if framework := detail.framework:
                self.framework.setCurrentText(framework)
            if language := detail.language:
                self.language.setCurrentText(language)
            if tool := detail.tool:
                self.tool.setCurrentText(tool)

            self.code_pager.clear_pages()
            for code_block in detail.code:
                self.code_pager.add_page(QCodeEdit(code_block.code, self), code_block.language)

        self.can_upload_code()
        self.generate_content.setEnabled(bool(self.image))
        self.generate_code.setEnabled(bool(self.image))

    def str_detail(self) -> str:
        """Convert the detail to a string."""
        text = ""
        if project := self.project.text():
            text += f"\nProject Folder: {project}"
        if location := self.location.text():
            text += f"\nFile Location: {location}"
        if framework := self.framework.currentText():
            text += f"\nUsing Framework: {framework}"
        if language := self.language.currentText():
            text += f"\nCode Language: {language}"
        if tool := self.tool.currentText():
            text += f"\nTest Tool: {tool}"
        if content := self.content.toPlainText():
            text += f"\nImage Content: {content}"

        source_code = Path(self.project.text()) / Path(self.location.text())
        if source_code.exists() and self.upload_code.isChecked():
            text += f"\nSource Code:\n{source_code.read_text()}"
        return text

    def sync_detail(self) -> None:
        with block_signals(self):
            self.detail = Detail(
                project=self.project.text().strip(),
                location=self.location.text().strip(),
                framework=self.framework.currentText().strip(),
                language=self.language.currentText().strip(),
                tool=self.tool.currentText().strip(),
                content=self.content.toPlainText().strip(),
                code=[CodeBlock(language=title.strip(), code=code.toPlainText().strip())
                      for title, code in self.code_pager.pages() if isinstance(code, QCodeEdit)]
            )
