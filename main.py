from PySide6 import QtWidgets
from mainwindow import Ui_MainWindow
from PySide6.QtCore import Qt
import sys
import threading
from nagi_native import PlatformLibrary
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent = parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(self.width(), self.height())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    PlatformLibrary.set_background_transparent(w.winId())
    sys.exit(app.exec())