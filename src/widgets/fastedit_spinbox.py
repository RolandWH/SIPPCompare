from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QSpinBox, QDoubleSpinBox


class FastEditQDoubleSpinBox(QDoubleSpinBox):
    def focusInEvent(self, e):
        QTimer.singleShot(0, self.selectAll)
        super(FastEditQDoubleSpinBox, self).focusInEvent(e)


class FastEditQSpinBox(QSpinBox):
    def focusInEvent(self, e):
        QTimer.singleShot(0, self.selectAll)
        super(FastEditQSpinBox, self).focusInEvent(e)
