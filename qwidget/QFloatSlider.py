from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSlider


class QFloatSlider(QSlider):
    valueChangedFloat = Signal(float)

    def __init__(self, parent=None, multiplier=100):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._multiplier = multiplier

        self.valueChanged.connect(self.on_value_changed)

    @property
    def float_value(self) -> float:
        return self.value() / self._multiplier

    @float_value.setter
    def float_value(self, value: float) -> None:
        int_value = int(value * self._multiplier)
        self.setValue(int_value)

    @property
    def multiplier(self) -> float:
        return self._multiplier

    @multiplier.setter
    def multiplier(self, multiplier: int) -> None:
        self._multiplier = multiplier

    def on_value_changed(self) -> None:
        self.valueChangedFloat.emit(self.float_value)
