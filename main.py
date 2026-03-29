from PySide6 import QtWidgets
from mainwindow import Ui_MainWindow
from PySide6.QtCore import Qt
import sys
from tray import SystemTray
from nagi_native import LAppLive2DManager, PlatformLibrary
from G import G
import os
os.environ["QT_OPENGL"] = "desktop"  # 或 "angle" 或 "software"
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent = parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(self.width(), self.height())

        # 系统托盘
        self.tray = SystemTray(self)
        self._setup_tray_connections()
        self.tray.show()

    def _setup_tray_connections(self):
        """设置托盘信号连接"""
        self.tray.show_window_triggered.connect(self.show_window)
        self.tray.hide_window_triggered.connect(self.hide)
        self.tray.quit_triggered.connect(QtWidgets.QApplication.quit)
        self.tray.topmost_triggered.connect(self.toggle_topmost)
        self.tray.change_model_triggered.connect(self._change_model)

    def _change_model(self, model_name):
        """切换模型"""
        LAppLive2DManager.ChangeScene(model_name)
        w.show()
    
    def toggle_topmost(self):
        """切换置顶状态"""
        checked = G.config.get("window_topmost")
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint.value
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint.value
        self.setWindowFlags(flags)
        self.show()
    
    def show_window(self):
        """显示窗口"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized)
        self.activateWindow()
    
    def closeEvent(self, event):
        """重写关闭事件，最小化到托盘"""
        if self.tray.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.widget.showBubbleText("你好")
    PlatformLibrary.set_background_transparent(w.winId())
    sys.exit(app.exec())