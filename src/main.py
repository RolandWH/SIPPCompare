## Nuitka compilation options (Windows only)
# nuitka-project: --mode=onefile
# nuitka-project: --enable-plugin=pyqt6
# nuitka-project: --include-module=widgets.mpl_widget
# nuitka-project: --include-data-files=icon2.ico=icon2.ico
# nuitka-project: --include-data-dir=gui=gui
# nuitka-project: --windows-console-mode=disable
# nuitka-project: --windows-icon-from-ico=icon2.ico
# nuitka-project: --product-name=SIPPCompare
# nuitka-project: --file-description=SIPPCompare
# nuitka-project: --product-version=1.1
# nuitka-project: --output-dir=build
# nuitka-project: --output-filename=SIPPCompare
import sys

from PyQt6.QtWidgets import QApplication

from main_window import SIPPCompare


app = QApplication(sys.argv)
window = SIPPCompare()
window.show()
app.exec()
