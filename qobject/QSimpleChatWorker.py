from typing import Optional

from PySide6.QtCore import QObject, QRunnable, Signal
from loguru import logger

from util import chat


class QSimpleChatWorkerSignals(QObject):
    finished = Signal(str)
    failed = Signal(Exception)


class QSimpleChatWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = QSimpleChatWorkerSignals()
        self._system = None
        self._text = None
        self._image = None

    @property
    def system(self) -> Optional[str]:
        return self._system

    @system.setter
    def system(self, system: Optional[str]):
        self._system = system

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text

    @property
    def image(self) -> Optional[str]:
        return self._image

    @image.setter
    def image(self, image: Optional[str]):
        self._image = image

    def run(self):
        try:
            result = chat(system=self.system, text=self.text, image_url=self.image)
            self.signals.finished.emit(result)
        except Exception as e:
            logger.error(f"Error while chatting: {e}")
            self.signals.failed.emit(e)
