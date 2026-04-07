from PySide6 import QtWidgets
from mainwindow import Ui_MainWindow
from PySide6.QtCore import Qt, QPoint, QMimeData
from PySide6.QtGui import QGuiApplication, QDragEnterEvent, QDropEvent
import sys
from tray import SystemTray
from network import NetworkController
from nagi_native import LAppLive2DManager, PlatformLibrary
from G import G
import os
os.environ["QT_OPENGL"] = "desktop"  # 或 "angle" 或 "software"
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent = parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setFixedSize(self.width(), self.height())

        # 窗口拖动相关
        self._drag_position = None
        self._is_movable = G.config.get("window_movable", True)

        # 恢复窗口位置
        self._restore_window_position()

        # 系统托盘
        self.tray = SystemTray(self)
        self._setup_tray_connections()
        self.tray.show()

        # 网络控制器
        self.network_controller = None
        self._setup_network()
        self.toggle_topmost()

        # 启用拖拽
        self.setAcceptDrops(True)

    def _setup_network(self):
        """设置网络控制器"""
        if G.config.get("network_enabled", True):
            host = G.config.get("network_host", "127.0.0.1")
            port = G.config.get("network_port", 9527)
            
            self.network_controller = NetworkController(host, port, self)
            self._setup_network_connections()
            self.network_controller.start()

    def _setup_network_connections(self):
        """设置网络控制器信号连接"""
        if self.network_controller:
            self.network_controller.show_window_requested.connect(self.show_window)
            self.network_controller.hide_window_requested.connect(self.hide)
            self.network_controller.show_bubble_requested.connect(self._show_bubble_from_network)
            self.network_controller.change_model_requested.connect(self._change_model)
            self.network_controller.set_topmost_requested.connect(self._set_topmost_from_network)
            self.network_controller.set_movable_requested.connect(self._on_movable_changed)
            self.network_controller.move_window_requested.connect(self._move_window_from_network)
            self.network_controller.reset_position_requested.connect(self._reset_window_position)
            self.network_controller.quit_requested.connect(QtWidgets.QApplication.quit)

    def _show_bubble_from_network(self, text: str, params: dict):
        """从网络请求显示气泡文字"""
        x = params.get("x")
        y = params.get("y")
        duration = params.get("duration", 2000)
        typing_speed = params.get("typing_speed", 50)
        max_width = params.get("max_width", 200)
        self.widget.showBubbleText(text, x, y, duration, typing_speed, max_width)

    def _set_topmost_from_network(self, enabled: bool):
        """从网络请求设置置顶"""
        G.config.set("window_topmost", enabled)
        # 同步更新托盘菜单状态
        if hasattr(self.tray, 'topmost_action'):
            self.tray.topmost_action.setChecked(enabled)
        self.toggle_topmost()

    def _move_window_from_network(self, x: int, y: int):
        """从网络请求移动窗口"""
        self.move(x, y)
        G.config.set("window_x", x)
        G.config.set("window_y", y)

    def _restore_window_position(self):
        """恢复窗口位置"""
        x = G.config.get("window_x")
        y = G.config.get("window_y")
        
        if x is not None and y is not None:
            # 确保窗口在屏幕范围内
            screen = QGuiApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            
            # 限制窗口位置在屏幕范围内
            x = max(0, min(x, screen_geometry.width() - self.width()))
            y = max(0, min(y, screen_geometry.height() - self.height()))
            
            self.move(x, y)

    def _reset_window_position(self):
        """重置窗口位置到屏幕中心"""
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        G.config.set("window_x", x)
        G.config.set("window_y", y)

    def _setup_tray_connections(self):
        """设置托盘信号连接"""
        self.tray.show_window_triggered.connect(self.show_window)
        self.tray.hide_window_triggered.connect(self.hide)
        self.tray.quit_triggered.connect(self._on_quit)
        self.tray.topmost_triggered.connect(self.toggle_topmost)
        self.tray.change_model_triggered.connect(self._change_model)
        self.tray.movable_triggered.connect(self._on_movable_changed)
        self.tray.reset_position_triggered.connect(self._reset_window_position)

    def _on_quit(self):
        """退出处理"""
        # 停止网络服务
        if self.network_controller:
            self.network_controller.stop()
        QtWidgets.QApplication.quit()

    def _on_movable_changed(self, movable):
        """窗口可移动状态改变"""
        self._is_movable = movable
        G.config.set("window_movable", movable)
        # 同步更新托盘菜单状态
        if hasattr(self.tray, 'movable_action'):
            self.tray.movable_action.setChecked(movable)

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
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖动"""
        if self._is_movable and event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if self._is_movable and self._drag_position is not None and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 结束拖动并保存位置"""
        if self._is_movable and event.button() == Qt.MouseButton.LeftButton and self._drag_position is not None:
            self._drag_position = None
            # 保存窗口位置到配置
            pos = self.pos()
            G.config.set("window_x", pos.x())
            G.config.set("window_y", pos.y())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def closeEvent(self, event):
        """重写关闭事件，最小化到托盘"""
        if self.tray.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            # 停止网络服务
            if self.network_controller:
                self.network_controller.stop()
            event.accept()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    files.append(url.toLocalFile())
            if files:
                self._on_files_dropped(files)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

    def _on_files_dropped(self, files: list):
        """处理拖拽的文件"""
        print(f"拖拽了 {len(files)} 个文件:")
        for f in files:
            print(f"  - {f}")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    w.widget.showBubbleText("你好11111111111111111111111aaaaaaa")
    PlatformLibrary.set_background_transparent(w.winId())
    sys.exit(app.exec())