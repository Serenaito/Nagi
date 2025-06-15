from PySide6 import QtWidgets
from mainwindow import Ui_MainWindow
from PySide6.QtCore import Qt
import sys
class Test(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(Test, self).__init__(parent = parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(self.width(), self.height())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Test()
    w.show()
    sys.exit(app.exec())