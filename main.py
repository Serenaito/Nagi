from PySide6 import QtWidgets
from untited import Ui_MainWindow
import sys
from nagi_native import nagi_cpp
class Test(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(Test, self).__init__(parent = parent)
        self.setupUi(self)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Test()
    w.show()
    sys.exit(app.exec())