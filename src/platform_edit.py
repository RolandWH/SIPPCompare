from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

class PlatformEdit(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/platform_edit.ui", self)
