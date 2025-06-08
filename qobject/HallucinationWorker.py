from PySide6.QtCore import QObject, QRunnable, Signal

from util import hallucination


class HallucinationWorkerSignals(QObject):
    """
    Signals for the HallucinationWorker
    """
    succeed = Signal(bool, list)


class HallucinationWorker(QRunnable):
    """
    Worker for hallucination
    """

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self.signals = HallucinationWorkerSignals()

    def run(self):
        try:
            result = hallucination(self.image_path)
            self.signals.succeed.emit(True, result)
        except Exception as _:
            self.signals.succeed.emit(False, [])
