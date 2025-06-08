import time
from pathlib import Path
from queue import Queue
from typing import List, Literal

from PySide6.QtCore import Slot, QThreadPool, QTimer, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog, QWidget, QPushButton, QDialogButtonBox, QMessageBox
from loguru import logger

import constant
from entity import SupportedImage
from qmessagebox import invalid_folder, task_completed, leave_while_running, overwrite_files, too_few_files
from qobject import QCancellableChatWorker
from qwindow import BatchContentUi
from util import read_settings, write_settings


# noinspection DuplicatedCode
class BatchContent(QDialog, BatchContentUi):
    WORKER_START_DELAY = 500

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setupUi(self)
        self._folder = None
        self._selected_images = []

        self._thread_pool = QThreadPool.globalInstance()
        self._start_timer = QTimer()

        self._workers: List[QCancellableChatWorker] = []
        self._worker_queue = Queue()

        self._is_running = False
        self._log_file = None

        self._finished_count = 0
        self._failed_count = 0
        self._canceled_count = 0

        self.__setup_ui_components()
        self.__connect_signals()

    @property
    def folder(self) -> Path | None:
        return self._folder

    @folder.setter
    def folder(self, value: Path) -> None:
        self._folder = value

    @property
    def selected_images(self) -> List[str]:
        return self._selected_images

    @selected_images.setter
    def selected_images(self, value: List[str]) -> None:
        self._selected_images = value

    def __setup_ui_components(self) -> None:
        self.check_box.setCheckState(read_settings('BatchContent', 'selected_images',
                                                   Qt.CheckState.Checked, type_=Qt.CheckState))

        self.start = QPushButton("Start")
        self.abort = QPushButton("Abort")
        self.cancel = QPushButton("Cancel")

        self.button_box.addButton(self.start, QDialogButtonBox.ButtonRole.ActionRole)
        self.button_box.addButton(self.abort, QDialogButtonBox.ButtonRole.DestructiveRole)
        self.button_box.addButton(self.cancel, QDialogButtonBox.ButtonRole.RejectRole)

        self.abort.setDisabled(True)

    def __connect_signals(self) -> None:
        self._start_timer.timeout.connect(self._start_next_worker)

        self.check_box.checkStateChanged.connect(self.on_check_box_check_state_changed)

        self.start.clicked.connect(self.on_start_clicked)
        self.abort.clicked.connect(self.on_abort_clicked)
        self.cancel.clicked.connect(self.on_cancel_clicked)

    def _check_completion(self, *, status: Literal["finished", "failed", "canceled"] = "failed") -> None:
        """
        Check if all tasks are completed
        """
        match status:
            case "finished":
                self._finished_count += 1
            case "failed":
                self._failed_count += 1
            case "canceled":
                self._canceled_count += 1
            case _:
                raise ValueError(f"Invalid status: {status}")

        if self._is_running:
            self.progress_bar.setValue(self.progress_bar.value() + 1)
        else:
            return

        # Check if all workers are finished
        if all(not w.is_alive() for w in self._workers):
            self._is_running = False
            self.abort.setDisabled(True)
            self.start.setEnabled(True)
            self.cancel.setEnabled(True)

            for w in self._workers:
                if w.is_finished():
                    w.detail.content = w.result
                    w.detail.save(w.json)

            task_completed(self,
                           message=f"Succeed: {self._finished_count}\rFailed: {self._failed_count}\rCanceled: {self._canceled_count}"
                                   f"\nTask log file is saved to {self._log_file}")
            logger.info("All tasks completed!")

    def _qt_message_handler(self, message) -> None:
        """
        Convert loguru levels to HTML colors
        """
        level_colors = {
            "INFO": "black",
            "SUCCESS": "green",
            "WARNING": "orange",
            "ERROR": "red",
        }
        level_name = message.record["level"].name
        color = level_colors.get(level_name, "black")
        html_message = f'<span style="color: {color};">{message}</span>'
        self.text_edit.append(html_message)

    def _reset_state(self):
        self.text_edit.clear()
        self.progress_bar.setValue(0)

        self._workers.clear()
        self._worker_queue = Queue()
        self._is_running = False
        self._finished_count = 0
        self._failed_count = 0
        self._canceled_count = 0

        logger.remove()

    def _start_next_worker(self):
        if not self._worker_queue.empty():
            self._thread_pool.start(self._worker_queue.get())
        else:
            self._start_timer.stop()

    def _setup_worker(self, index: int, image: Path) -> QCancellableChatWorker:
        worker = QCancellableChatWorker()
        worker.system = read_settings('Prompt', 'content', default=constant.PROMPT_CONTENT)
        worker.text = None
        worker.image = str(image.absolute())
        worker.index = index

        # Connect signals
        worker.signals.finished.connect(self.on_worker_finished)
        worker.signals.failed.connect(self.on_worker_failed)
        worker.signals.canceled.connect(self.on_worker_canceled)

        return worker

    def _notify_before_exiting(self, event: QCloseEvent = None):
        if self._is_running and QMessageBox.StandardButton.Yes == \
                leave_while_running(self, message="Tasks are still running. Do you want to abort and close?"):
            self.on_abort_clicked(True)
        else:
            if event:
                event.ignore()

    @Slot(int)
    def on_check_box_check_state_changed(self, state: int) -> None:
        write_settings('BatchContent', 'selected_images', state)

    @Slot(bool)
    def on_start_clicked(self, _: bool) -> None:
        if not self.folder:
            invalid_folder(self)
            return

        if QMessageBox.StandardButton.No == overwrite_files(self,
                                                            message="This action will OVERWRITE all existing image contents. Continue?"):
            return

        # Reset state
        self._reset_state()

        # Setup logging
        self._log_file = f"batch_content_{time.strftime('%Y_%m_%d_%H_%M_%S')}.log"
        logger.add(self._qt_message_handler)
        logger.add(open(self._log_file, "w"))
        logger.info(f"Starting... Log file is saved to {self._log_file}")

        # Process images
        if self.check_box.checkState() == Qt.CheckState.Checked:
            if not self.selected_images:
                too_few_files(self, message="Please select at least one image")
                return
            images = [self.folder / f for f in self.selected_images if SupportedImage(self.folder / f).is_supported()]
        else:
            images = [f for f in self.folder.glob("*.*") if SupportedImage(f).is_supported()]
        logger.info(f"Found {len(images)} images to process")
        self.progress_bar.setMaximum(len(images))
        for index, image in enumerate(images):
            try:
                worker = self._setup_worker(index, image)
                self._workers.append(worker)
                self._worker_queue.put(worker)
            except Exception as e:
                logger.error(f"Failed to initialize worker {index}: {e}")

        if not self._workers:
            logger.error("No valid workers created!")
            return

        # Start processing
        logger.info(f"Starting {len(self._workers)} workers...")
        self._start_timer.start(self.WORKER_START_DELAY)

        # Update UI state
        self._is_running = True
        self.start.setDisabled(True)
        self.abort.setEnabled(True)
        self.cancel.setDisabled(True)

    @Slot(bool)
    def on_abort_clicked(self, _: bool) -> None:
        self._start_timer.stop()

        for worker in self._workers:
            worker.cancel()
        while not self._worker_queue.empty():
            self._worker_queue.get().cancel()
        self._worker_queue = Queue()

        logger.warning("User aborted...")

    @Slot(bool)
    def on_cancel_clicked(self, _: bool) -> None:
        """
        Handle the cancellation of the batch content
        """
        self._notify_before_exiting()
        self.close()

    @Slot(int, str, str)
    def on_worker_finished(self, index: int, image_path: str, _: str) -> None:
        """
        Handle the completion of a worker
        """
        logger.success(f"{index}: {image_path} finished!")
        self._check_completion(status="finished")

    @Slot(int, str, Exception)
    def on_worker_failed(self, index: int, image_path: str, error: Exception) -> None:
        """
        Handle the failure of a worker
        """
        error_msg = str(error)
        if hasattr(error, 'with_traceback'):
            logger.error(f"{index}: {image_path} failed! Error: {error_msg}\n{error.with_traceback(None)}")
        else:
            logger.error(f"{index}: {image_path} failed! Error: {error_msg}")
        self._check_completion(status="failed")

    @Slot(int, str)
    def on_worker_canceled(self, index: int, image_path: str) -> None:
        """
        Handle the cancellation of a worker
        """
        logger.warning(f"{index}: {image_path} canceled!")
        self._check_completion(status="canceled")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle the close event of the batch content
        """
        self._notify_before_exiting(event)
        event.accept()
