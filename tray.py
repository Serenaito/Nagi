# -*- coding: utf-8 -*-
"""系统托盘模块"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QActionGroup
from PySide6.QtCore import QObject, Signal
from config import Config
from G import G
class SystemTray(QObject):
    """系统托盘类"""

    # 信号
    show_window_triggered = Signal()
    hide_window_triggered = Signal()
    quit_triggered = Signal()
    topmost_triggered = Signal()
    change_model_triggered = Signal(str)

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.parent = parent
        self.tray_icon = QSystemTrayIcon(parent)
        self._setup_tray()
    
    def _setup_tray(self):
        """设置系统托盘"""
        # 设置托盘图标
        icon = QIcon()
        # 使用默认图标，可以替换为自定义图标
        icon.addPixmap(self._create_default_icon())
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Nagi")
        
        # 创建右键菜单
        self._create_context_menu()
        
        # 连接信号
        self.tray_icon.activated.connect(self._on_tray_activated)
    
    def _create_default_icon(self):
        """创建默认托盘图标"""
        from PySide6.QtGui import QPixmap, QPainter, QColor
        from PySide6.QtCore import Qt
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(70, 130, 180))  # 钢蓝色
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        painter.end()
        return pixmap
    
    def _create_context_menu(self):
        """创建右键菜单"""
        menu = QMenu()

        # 模型切换子菜单
        self.model_menu = menu.addMenu("切换模型")
        self.models = G.config.get_available_models()
        self.model_action_group = QActionGroup(self)
        self.model_action_group.setExclusive(True)

        current_model = G.config.get("current_model", "")
        for model_name in self.models:
            action = QAction(model_name, self)
            action.setCheckable(True)
            action.setData(model_name)
            # 根据配置设置当前模型
            if current_model and current_model == model_name:
                action.setChecked(True)
            elif not current_model and model_name == self.models[0]:
                action.setChecked(True)
            action.triggered.connect(lambda checked, name=model_name: self._change_model(name))
            self.model_action_group.addAction(action)
            self.model_menu.addAction(action)

        menu.addSeparator()

        # 显示窗口动作
        self.show_action = QAction("显示窗口", menu)
        self.show_action.triggered.connect(self.show_window_triggered.emit)
        menu.addAction(self.show_action)

        # 隐藏窗口动作
        self.hide_action = QAction("隐藏窗口", menu)
        self.hide_action.triggered.connect(self.hide_window_triggered.emit)
        menu.addAction(self.hide_action)

        menu.addSeparator()

        # 置顶动作
        self.topmost_action = QAction("置顶", menu)
        self.topmost_action.setCheckable(True)
        self.topmost_action.setChecked(G.config.get("window_topmost", False))
        self.topmost_action.triggered.connect(self._on_topmost_toggled)
        menu.addAction(self.topmost_action)

        menu.addSeparator()

        # 退出动作
        self.quit_action = QAction("退出", menu)
        self.quit_action.triggered.connect(self.quit_triggered.emit)
        menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(menu)

    def _change_model(self, model_name):
        """切换模型"""
        # 更新配置
        G.config.set("current_model", model_name)
        
        # 发送信号通知切换模型
        self.change_model_triggered.emit(model_name)
    
    def _on_tray_activated(self, reason):
        """托盘图标被激活时的处理"""
        from PySide6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # 双击托盘图标，切换显示/隐藏状态
            self.show_window_triggered.emit()

    def _on_topmost_toggled(self, checked):
        """置顶状态切换处理"""
        G.config.set("window_topmost", checked)
        self.topmost_triggered.emit()

    def show(self):
        """显示托盘图标"""
        self.tray_icon.show()
    
    def hide(self):
        """隐藏托盘图标"""
        self.tray_icon.hide()
    
    def set_icon(self, icon):
        """设置托盘图标"""
        self.tray_icon.setIcon(icon)
    
    def set_tooltip(self, tooltip):
        """设置托盘提示"""
        self.tray_icon.setToolTip(tooltip)
