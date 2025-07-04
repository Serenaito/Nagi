from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter,QColor
from nagi_native import LAppDelegate,LAppWindow
import math
class QModelWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(QModelWidget, self).__init__(parent = parent)
        LAppDelegate.Initialize(LAppWindow(self))
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def initializeGL(self):
        LAppDelegate.Initialize(LAppWindow(self))
 
    def paintGL(self):
        LAppDelegate.update()

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
