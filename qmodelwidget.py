from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import QTimer
from nagi_native import LAppDelegate, LAppWindow
from G import G
from bubble_text import BubbleManager


class QModelWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(QModelWidget, self).__init__(parent=parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)
        self.bubble_manager = BubbleManager(self)

    def initializeGL(self):
        LAppDelegate.Initialize(LAppWindow(self), G.config.get_current_mode())

    def resizeGL(self, w, h):
        pass
        # LAppDelegate.resize(w, h)
    
    def mouseReleaseEvent(self, event):
        LAppDelegate.mouseReleaseEvent(event.x(), event.y())
        return super().mouseReleaseEvent(event)
    
    def mousePressEvent(self, event):
        LAppDelegate.mousePressEvent(event.x(), event.y())
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        LAppDelegate.mouseMoveEvent(event.x(), event.y())
        return super().mouseMoveEvent(event)

    def showBubbleText(self, text, x=None, y=None, duration=2000, typing_speed=50, max_width=200, **kwargs):
        """
        显示气泡文字（带打字机效果，支持自动换行）
        
        Args:
            text: 要显示的文字内容
            x: 气泡的 x 坐标，如果为 None 则居中显示
            y: 气泡的 y 坐标，如果为 None 则显示在顶部
            duration: 文字全部显示完后的持续时长 (毫秒)
            typing_speed: 打字机效果的速度，每个字符出现的间隔时间 (毫秒)
            max_width: 气泡最大宽度 (像素)，超过此宽度自动换行，默认 200
            **kwargs: 其他参数传递给 BubbleText (bg_color, text_color, font_size)
        """
        self.bubble_manager.show_bubble(text, x, y, duration, typing_speed, max_width, **kwargs)

    def paintGL(self):
        LAppDelegate.update()
        self.bubble_manager.update()
        self.bubble_manager.draw()