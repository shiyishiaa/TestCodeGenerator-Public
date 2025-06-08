from pathlib import Path
from typing import Optional, Dict, Any, List

from PySide6.QtCore import Qt, Slot, QTimer, QThreadPool
from PySide6.QtGui import QCloseEvent, QShortcut, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QListWidgetItem, QTableWidgetItem, QApplication

from constant import APPLICATION, PROMPT_CONTENT, PROMPT_CODE, PROMPT_RELATED
from entity import ImageFileInfo, Detail, ModelSettings, ModelProvider, SupportedImage
from qmessagebox import failed_to_generate, failed_to_save, invalid_file, save_changes, leave_without_saving, \
    too_few_files, too_many_files, failed_to_hallucinate
from qobject import QSimpleChatWorker, HallucinationWorker
from qwindow import MainWindowUi
from util import analyze_image_file, read_settings, write_settings, extract_code_blocks, read_model_settings
from .BatchCode import BatchCode
from .BatchContent import BatchContent
from .SettingsModel import SettingsModel
from .SettingsPrompt import SettingsPrompt


class MainWindow(QMainWindow, MainWindowUi):
    # ------------------------------------------------slots------------------------------------------------

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowState(Qt.WindowState.WindowMaximized)

        # State variables
        self.folder_path: Optional[Path] = None
        self.image_path: Optional[SupportedImage] = None
        self.json_path: Optional[Path] = None
        self.hallucination_result: Optional[List[bool]] = None
        self.is_edited: bool = False
        self.shift_start_index: Optional[int] = None
        self.shift_end_index: Optional[int] = None

        # Shortcuts
        self.shortcut_next = QShortcut(QKeySequence(Qt.Key.Key_Down), self.window())
        self.shortcut_prev = QShortcut(QKeySequence(Qt.Key.Key_Up), self.window())

        # Cache for model settings
        self._model_settings: Optional[ModelSettings] = None
        self._image_info_cache: Dict[str, ImageFileInfo] = {}

        self.__setup_ui_components()
        self.__connect_signals()

    # ------------------------------------------------properties------------------------------------------------

    @property
    def model_settings(self) -> ModelSettings:
        """Cached model settings"""
        if self._model_settings is None:
            self._model_settings = read_model_settings()
        return self._model_settings

    # ------------------------------------------------static methods------------------------------------------------

    @staticmethod
    def __invert_check_state(item: QListWidgetItem) -> None:
        """Invert the check state of the item"""
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    # ------------------------------------------------private methods------------------------------------------------

    def __setup_ui_components(self) -> None:
        """Initialize UI components"""
        self.setWindowTitle(self._build_window_title())
        self.line_edit_filename.setReadOnly(True)

        """Setup metadata table with model fields"""
        model_fields = [f.title() for f in ImageFileInfo.__pydantic_fields__.keys()]
        self.table_widget_metadata.setRowCount(len(model_fields))
        self.table_widget_metadata.setVerticalHeaderLabels(model_fields)
        self.table_widget_metadata.setColumnCount(1)
        self.table_widget_metadata.setHorizontalHeaderLabels(['Details'])

    # noinspection DuplicatedCode
    def __connect_signals(self) -> None:
        """Connect all signals and slots"""
        # Menu actions
        self.action_open.triggered.connect(self.on_action_open_triggered)
        self.action_open_last.triggered.connect(self.on_action_open_last_triggered)
        self.action_model.triggered.connect(self.on_action_model_triggered)
        self.action_prompt.triggered.connect(self.on_action_prompt_triggered)
        self.action_batch_content.triggered.connect(self.on_action_batch_content_triggered)
        self.action_batch_code.triggered.connect(self.on_action_batch_code_triggered)
        self.action_related_content.triggered.connect(self.on_action_related_content_triggered)
        self.action_related_code.triggered.connect(self.on_action_related_code_triggered)

        # UI elements
        self.push_button_select_all.clicked.connect(self.on_push_button_select_all_clicked)
        self.push_button_select_none.clicked.connect(self.on_push_button_select_none_clicked)
        self.list_widget_files.currentItemChanged.connect(self.on_list_widget_files_current_item_changed)
        self.list_widget_files.itemClicked.connect(self.on_list_widget_files_item_clicked)
        self.list_widget_files.itemDoubleClicked.connect(self.on_list_widget_files_double_clicked)
        self.push_button_hallucination.clicked.connect(self.on_push_button_hallucination_clicked)
        self.push_button_save.clicked.connect(self.on_push_button_save_clicked)
        self.detail_widget.detailEdited.connect(self.on_detail_edited)

        # Shortcuts
        self.shortcut_next.activated.connect(self.on_shortcut_next_triggered)
        self.shortcut_prev.activated.connect(self.on_shortcut_prev_triggered)

    # ------------------------------------------------protected methods------------------------------------------------

    # noinspection DuplicatedCode

    def _get_model_for_provider(self, provider: ModelProvider) -> Any:
        """Get model setting for current provider"""
        match provider:
            case ModelProvider.Claude:
                return self.model_settings.claude_model
            case ModelProvider.SiliconFlow:
                return self.model_settings.siliconflow_model
            case _:
                return self.model_settings.openai_model

    def _build_window_title(self) -> str:
        """Build window title with current state"""
        provider = self.model_settings.provider
        model = self._get_model_for_provider(provider)
        return (f'{APPLICATION} '
                f'- [{provider.value}/{model} enabled] '
                f'- {str(self.image_path) if self.image_path else "No file selected"}'
                f'{" - Edited" if self.is_edited else ""}')

    def _load_folder(self) -> None:
        """Load image from selected folder into list widget"""
        self.list_widget_files.clear()
        for image_path in [SupportedImage(f) for f in self.folder_path.glob("*") if SupportedImage(f).is_supported()]:
            item = QListWidgetItem(image_path.name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.list_widget_files.addItem(item)

    def _load_image(self) -> None:
        """Load image into graphics view"""
        self.graphics_view_image.load_image(str(self.image_path))

    def _load_metadata(self) -> None:
        """Load image metadata into panel"""
        self.line_edit_filename.setText(self.image_path.name)

        # Load metadata with caching
        image_file_info = self._get_cached_image_info()
        if not image_file_info.is_valid:
            invalid_file(self)
            return

        self._update_metadata_table(image_file_info)
        self.detail_widget.image = str(self.image_path)
        self.detail_widget.detail = Detail.load(str(self.json_path))

    def _get_cached_image_info(self) -> ImageFileInfo:
        """Get cached image info or analyze and cache"""
        image_path_str = str(self.image_path.resolve())
        if image_path_str not in self._image_info_cache:
            self._image_info_cache[image_path_str] = analyze_image_file(self.image_path)
        return self._image_info_cache[image_path_str]

    def _update_metadata_table(self, image_file_info: ImageFileInfo) -> None:
        """Update metadata table with image info"""
        for i in range(self.table_widget_metadata.rowCount()):
            header = self.table_widget_metadata.verticalHeaderItem(i)
            val = str(getattr(image_file_info, header.text().lower()))
            item = QTableWidgetItem(val, QTableWidgetItem.ItemType.UserType)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_widget_metadata.setItem(i, 0, item)
        self.table_widget_metadata.resizeColumnsToContents()

    # ------------------------------------------------qt slots------------------------------------------------

    @Slot(bool)
    def on_action_open_triggered(self, _: bool) -> None:
        """Open a new folder through file dialog"""
        if selected_folder := QFileDialog.getExistingDirectory(self, 'Select Folder'):
            self.folder_path = Path(selected_folder)
            self._load_folder()
            write_settings('Folder', 'last_folder', selected_folder)

    @Slot(bool)
    def on_action_open_last_triggered(self, _: bool) -> None:
        """Open the last used folder from config"""
        self.folder_path = Path(read_settings('Folder', 'last_folder', Path(__file__).parent, type_=Path))
        self._load_folder()

    @Slot(bool)
    def on_push_button_hallucination_clicked(self, _: bool) -> None:
        """Check if the test code is correct and the hallucination not exists in the test code given the screenshot and source code."""
        if not self.image_path:
            invalid_file(self)
            return

        self.label_hallucination.setText("<html><body><p style='color: gray;'>Checking...</p></body></html>")

        worker = HallucinationWorker(self.image_path)
        worker.signals.succeed.connect(self.on_hallucination_worker_succeed)
        QThreadPool.globalInstance().start(worker)

    @Slot(bool)
    def on_push_button_save_clicked(self, _: bool) -> None:
        """Save changes to the description file"""
        self.detail_widget.sync_detail()
        if not (detail := self.detail_widget.detail) or not self.json_path:
            return

        try:
            detail.save(self.json_path)
            self.setWindowTitle(self._build_window_title())
            self.detail_widget.location.setStyleSheet("")
            self.detail_widget.detailEdited.emit(False)
        except Exception as e:
            failed_to_save(self, exception=e)

    @Slot(bool)
    def on_detail_edited(self, edited: bool) -> None:
        """Update state when content is edited"""
        self.is_edited = edited
        self.setWindowTitle(self._build_window_title())
        self.detail_widget.sync_detail()

    @Slot(bool)
    def on_action_model_triggered(self, _: bool) -> None:
        """Open model settings dialog"""
        SettingsModel(self).exec()
        self._model_settings = read_model_settings()
        self.setWindowTitle(self._build_window_title())

    @Slot(bool)
    def on_action_prompt_triggered(self, _: bool) -> None:
        """Open prompt settings dialog"""
        SettingsPrompt(self).show()

    @Slot(bool)
    def on_action_batch_content_triggered(self, _: bool) -> None:
        """Open batch content dialog"""
        batch_content = BatchContent(self)
        batch_content.folder = self.folder_path
        batch_content.selected_images = [self.list_widget_files.item(i).text()
                                         for i in range(self.list_widget_files.count())
                                         if self.list_widget_files.item(i).checkState() == Qt.CheckState.Checked]
        batch_content.exec()

    @Slot(bool)
    def on_action_batch_code_triggered(self, _: bool) -> None:
        """Open batch code dialog"""
        batch_code = BatchCode(self)
        batch_code.folder = self.folder_path
        batch_code.selected_images = [self.list_widget_files.item(i).text()
                                      for i in range(self.list_widget_files.count())
                                      if self.list_widget_files.item(i).checkState() == Qt.CheckState.Checked]
        batch_code.exec()

    @Slot(bool)
    def on_push_button_select_all_clicked(self, _: bool) -> None:
        """Select all files in the list"""
        for i in range(self.list_widget_files.count()):
            self.list_widget_files.item(i).setCheckState(Qt.CheckState.Checked)

    @Slot(bool)
    def on_push_button_select_none_clicked(self, _: bool) -> None:
        """Select none files in the list"""
        for i in range(self.list_widget_files.count()):
            self.list_widget_files.item(i).setCheckState(Qt.CheckState.Unchecked)

    @Slot(QListWidgetItem)
    def on_list_widget_files_item_clicked(self, item: QListWidgetItem) -> None:
        """Handle click on a file from the list"""
        # if CTRL is pressed, select/deselect the item
        if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
            self.__invert_check_state(item)

        # if SHIFT is pressed, select the range of items between the current item and the clicked item
        elif QApplication.keyboardModifiers() == Qt.KeyboardModifier.ShiftModifier:
            if self.shift_start_index is None:
                self.shift_start_index = self.list_widget_files.row(item)
            self.shift_end_index = self.list_widget_files.row(item)

            self.shift_start_index = min(self.shift_start_index, self.shift_end_index)
            self.shift_end_index = max(self.shift_start_index, self.shift_end_index)

            for i in range(self.shift_start_index, self.shift_end_index + 1):
                self.list_widget_files.item(i).setCheckState(Qt.CheckState.Checked)
        else:
            self.shift_start_index = None
            self.shift_end_index = None

    @Slot(QListWidgetItem, QListWidgetItem)
    def on_list_widget_files_current_item_changed(self, current: QListWidgetItem, _: QListWidgetItem) -> None:
        """Handle selection of a file from the list (pathlib optimized)"""
        if self.is_edited and QMessageBox.StandardButton.Cancel == leave_without_saving(self):
            return

        selected_name = Path(current.text())

        # Enhanced security check using pathlib
        try:
            resolved_path = (self.folder_path / selected_name).resolve()
            if not resolved_path.is_relative_to(self.folder_path):
                raise ValueError("Path traversal attempt detected")
        except (ValueError, RuntimeError):
            invalid_file(self)
            return

        image_path = self.folder_path / selected_name.name
        json_path = image_path.with_suffix(image_path.suffix + '.json')

        if not image_path.exists():
            invalid_file(self)
            return

        if not json_path.exists():
            json_path.touch()
            json_path.write_text('{}')

        self.image_path = image_path
        self.json_path = json_path
        self.is_edited = False
        self.setWindowTitle(self._build_window_title())
        self.label_hallucination.setText("<html><body><p style='color: black;'>Not detected</p></body></html>")

        # Load image and metadata in parallel
        QTimer.singleShot(0, lambda: self._load_image())
        QTimer.singleShot(0, lambda: self._load_metadata())

    @Slot(QListWidgetItem)
    def on_list_widget_files_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double click on a file from the list"""
        self.__invert_check_state(item)

    # noinspection DuplicatedCode
    @Slot(bool)
    def on_action_related_content_triggered(self, _: bool) -> None:
        """Generate related content for selected files"""
        if self.is_edited and QMessageBox.StandardButton.Cancel == leave_without_saving(self):
            return

        checked_items = [self.list_widget_files.item(i)
                         for i in range(self.list_widget_files.count())
                         if self.list_widget_files.item(i).checkState() == Qt.CheckState.Checked]
        if not checked_items or len(checked_items) <= 1:
            too_few_files(self, message="Please select at least two files!")
            return

        if len(checked_items) > 5:
            too_many_files(self, message="Max 5 files are allowed!")
            return

        def _worker_finished(text: str) -> None:
            """Handle finished signal from worker"""
            for item in checked_items:
                json_path = str(self.folder_path / (item.text() + ".json"))
                detail = Detail.load(json_path)
                detail.content = text
                detail.save(json_path)

                if item == self.list_widget_files.currentItem():
                    self.detail_widget.detail = detail

            self.window().setEnabled(True)

        def _worker_failed(exception: Exception) -> None:
            """Handle failed signal from worker"""
            failed_to_generate(self, exception=exception)
            self.window().setEnabled(True)

        worker = QSimpleChatWorker()
        worker.system = read_settings('Prompt', 'content', default=PROMPT_CONTENT) + PROMPT_RELATED
        worker.text = self.detail_widget.str_detail()
        worker.image = [str((self.folder_path / item.text()).resolve()) for item in checked_items]
        worker.signals.finished.connect(_worker_finished)
        worker.signals.failed.connect(_worker_failed)
        QThreadPool.globalInstance().start(worker)

        self.window().setDisabled(True)

    # noinspection DuplicatedCode
    @Slot(bool)
    def on_action_related_code_triggered(self, _: bool) -> None:
        """Generate related code for selected files"""
        if self.is_edited and QMessageBox.StandardButton.Cancel == leave_without_saving(self):
            return

        checked_items = [self.list_widget_files.item(i)
                         for i in range(self.list_widget_files.count())
                         if self.list_widget_files.item(i).checkState() == Qt.CheckState.Checked]
        if not checked_items or len(checked_items) <= 1:
            too_few_files(self, message="Please select at least two files!")
            return

        if len(checked_items) > 5:
            too_many_files(self, message="Max 5 files are allowed!")
            return

        def _worker_finished(text: str) -> None:
            """Handle finished signal from worker"""
            for item in checked_items:
                json_path = str(self.folder_path / (item.text() + ".json"))
                detail = Detail.load(json_path)
                detail.code = extract_code_blocks(text)
                detail.save(json_path)

                if item == self.list_widget_files.currentItem():
                    self.detail_widget.detail = detail

            self.window().setEnabled(True)

        def _worker_failed(exception: Exception) -> None:
            """Handle failed signal from worker"""
            failed_to_generate(self, exception=exception)
            self.window().setEnabled(True)

        worker = QSimpleChatWorker()
        worker.system = read_settings('Prompt', 'code', default=PROMPT_CODE) + PROMPT_RELATED
        worker.text = self.detail_widget.str_detail()
        worker.image = [str((self.folder_path / item.text()).resolve()) for item in checked_items]
        worker.signals.finished.connect(_worker_finished)
        worker.signals.failed.connect(_worker_failed)
        QThreadPool.globalInstance().start(worker)

        self.window().setDisabled(True)

    @Slot()
    def on_shortcut_next_triggered(self) -> None:
        """Handle next file shortcut"""
        count = self.list_widget_files.count()
        if count == 0:
            return

        current_index = self.list_widget_files.currentRow()
        next_index = (current_index + 1) % count
        self.list_widget_files.setCurrentRow(next_index)

    @Slot()
    def on_shortcut_prev_triggered(self) -> None:
        """Handle previous file shortcut"""
        count = self.list_widget_files.count()
        if count == 0:
            return

        current_index = self.list_widget_files.currentRow()
        prev_index = (current_index - 1) % count
        self.list_widget_files.setCurrentRow(prev_index)

    # ------------------------------------------------signals------------------------------------------------

    @Slot(bool)
    def on_hallucination_finished(self, result: bool) -> None:
        """Handle hallucination finished signal"""

    @Slot(bool, list)
    def on_hallucination_worker_succeed(self, succeed: bool, result: list) -> None:
        """Handle hallucination succeed signal"""
        if succeed:
            self.hallucination_result = result
            if not self.hallucination_result:
                return

            index = self.detail_widget.code_pager.current_index
            if index is None:
                return

            if self.hallucination_result[index]:
                self.label_hallucination.setText(
                    "<html><body><p style='color: red;'>Hallucination detected!</p></body></html>")
            else:
                self.label_hallucination.setText(
                    "<html><body><p style='color: green;'>No hallucination detected!</p></body></html>")

        else:
            failed_to_hallucinate(self)

    # ------------------------------------------------qt events------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close events"""
        if not self.is_edited:
            event.accept()
            return

        reply = save_changes(self)

        if reply == QMessageBox.StandardButton.Yes:
            self.push_button_save.click()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()
