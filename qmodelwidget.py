from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import QTimer, QRectF
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QFont
from nagi_native import LAppDelegate,LAppWindow
import math

class BubbleText:
    """气泡文字类，存储气泡的显示信息"""
    def __init__(self, text, x, y, duration=2000, bg_color=QColor(255, 255, 255, 200), 
                 text_color=QColor(0, 0, 0), font_size=12):
        self.text = text
        self.x = x  # 相对于 widget 的 x 坐标
        self.y = y  # 相对于 widget 的 y 坐标
        self.duration = duration  # 显示时长 (毫秒)
        self.elapsed = 0  # 已经过的时间
        self.bg_color = bg_color
        self.text_color = text_color
        self.font_size = font_size
        self.padding = 8  # 文字内边距

class QModelWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(QModelWidget, self).__init__(parent = parent)
        LAppDelegate.Initialize(LAppWindow(self))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)
        self.bubbles = []  # 存储当前显示的气泡文字

    def initializeGL(self):
        LAppDelegate.Initialize(LAppWindow(self))

    def resizeGL(self, w, h):
        LAppDelegate.resize(w, h)
    
    def mouseReleaseEvent(self, event):
        LAppDelegate.mouseReleaseEvent(event.x(), event.y())
        return super().mouseReleaseEvent(event)
    
    def mousePressEvent(self, event):
        LAppDelegate.mousePressEvent(event.x(), event.y())
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        LAppDelegate.mouseMoveEvent(event.x(), event.y())
        return super().mouseMoveEvent(event)

    def showBubbleText(self, text, x=None, y=None, duration=2000, **kwargs):
        """
        显示气泡文字
        
        Args:
            text: 要显示的文字内容
            x: 气泡的 x 坐标，如果为 None 则居中显示
            y: 气泡的 y 坐标，如果为 None 则显示在顶部
            duration: 显示时长 (毫秒)
            **kwargs: 其他参数传递给 BubbleText (bg_color, text_color, font_size)
        """
        if x is None:
            x = self.width() // 2
        if y is None:
            y = 50
        bubble = BubbleText(text, x, y, duration, **kwargs)
        self.bubbles.append(bubble)

    def _updateBubbles(self):
        """更新气泡状态，移除已过期的气泡"""
        delta = 33  # 约 33ms 每帧
        for bubble in self.bubbles[:]:
            bubble.elapsed += delta
            if bubble.elapsed >= bubble.duration:
                self.bubbles.remove(bubble)

    def _drawBubbles(self):
        """绘制所有气泡文字"""
        if not self.bubbles:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for bubble in self.bubbles:
            # 计算淡出效果
            alpha_ratio = 1.0
            remaining = bubble.duration - bubble.elapsed
            if remaining < 500:
                alpha_ratio = remaining / 500
            
            # 准备字体
            font = QFont("Microsoft YaHei", bubble.font_size)
            painter.setFont(font)
            
            # 计算文字边界
            text_rect = painter.fontMetrics().boundingRect(bubble.text)
            text_width = text_rect.width()
            text_height = text_rect.height()
            
            # 计算气泡背景矩形
            rect_width = text_width + bubble.padding * 2
            rect_height = text_height + bubble.padding
            rect_x = bubble.x - rect_width // 2
            rect_y = bubble.y - rect_height
            
            # 绘制气泡背景 (圆角矩形)
            bg_color = QColor(bubble.bg_color)
            bg_color.setAlpha(int(bg_color.alpha() * alpha_ratio))
            painter.setBrush(bg_color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRectF(rect_x, rect_y, rect_width, rect_height), 10, 10)
            
            # 绘制文字
            text_color = QColor(bubble.text_color)
            text_color.setAlpha(int(text_color.alpha() * alpha_ratio))
            painter.setPen(text_color)
            painter.drawText(QRectF(rect_x, rect_y, rect_width, rect_height), 
                           Qt.AlignCenter, bubble.text)
        
        painter.end()

    def paintGL(self):
        LAppDelegate.update()
        self._updateBubbles()
        self._drawBubbles()
