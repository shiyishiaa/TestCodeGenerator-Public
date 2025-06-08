from typing import Literal, Optional

from PySide6.QtCore import QObject, Signal, QRunnable
from loguru import logger

from entity import Detail, SupportedImage
from util import chat


class QCancellableChatWorkerSignals(QObject):
    canceled = Signal(int, str)  # index, image_path
    finished = Signal(int, str, str)  # index, image_path, result
    failed = Signal(int, str, Exception)  # index, image_path, error


class QCancellableChatWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = QCancellableChatWorkerSignals()

        # Properties
        self._index = -1
        self._image = None
        self._json = None
        self._detail = None
        self._system = None
        self._text = None
        self._result = None

        # Status
        self._alive = False
        self._finished = False
        self._failed = False
        self._canceled = False

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, index: int):
        self._index = index

    @property
    def image(self) -> Optional[str]:
        return self._image

    @image.setter
    def image(self, value: Optional[str]):
        if value and SupportedImage(value).is_supported():
            self._image = value

    @property
    def json(self) -> str:
        if self._json:
            return self._json
        image_path = SupportedImage(self.image)
        if image_path.is_supported() and (json_file := image_path.with_suffix(image_path.suffix + ".json")):
            self._json = str(json_file)
            return self._json
        raise ValueError(f"Image {self.image} is not supported")

    @json.setter
    def json(self, value: str):
        self._json = value

    @property
    def detail(self) -> Detail:
        if self._detail:
            return self._detail
        try:
            self._detail = Detail.load(self.json)
            return self._detail
        except Exception as e:
            logger.error(f"Failed to load detail for {self.image}: {e}")
            self._detail = Detail()
            return self._detail

    @detail.setter
    def detail(self, detail: Detail):
        self._detail = detail

    @property
    def system(self) -> Optional[str]:
        return self._system

    @system.setter
    def system(self, value: Optional[str]):
        self._system = value

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    @property
    def result(self) -> Optional[str]:
        return self._result

    def _update_status(self, *, status: Literal["finished", "failed", "canceled"] = "failed"):
        """
        Update the status of the worker

        Args:
            status: The status of the worker.
        """
        match status:
            case "finished":
                self._finished = True
            case "failed":
                self._failed = True
            case "canceled":
                self._canceled = True

    def run(self):
        try:
            self._alive = True
            if not self.text and not self.image:
                raise ValueError(f"Worker {self.index}: Missing text and image configuration")

            logger.trace(f"Worker {self.index} running: {self.system}")
            logger.trace(f"Worker {self.index} running: {self.image}")
            logger.trace(f"Worker {self.index} running: {self.text}")
            result = chat(system=self.system, text=self.text, image_url=self.image)

            if self.is_canceled():
                self.signals.canceled.emit(self.index, self.image)
                self._update_status(status="canceled")
            else:
                self.signals.finished.emit(self.index, self.image, result)
                self._update_status(status="finished")
                self._result = result
        except Exception as e:
            logger.error(f"Worker {self.index} failed: {e}")
            self.signals.failed.emit(self.index, self.image or "", e)
            self._update_status(status="failed")
        finally:
            self._alive = False

    def is_alive(self) -> bool:
        return self._alive

    def is_finished(self) -> bool:
        return self._finished

    def is_failed(self) -> bool:
        return self._failed

    def is_canceled(self) -> bool:
        return self._canceled

    def cancel(self):
        self._canceled = True
