from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter,QColor
from nagi_native import nagi_cpp
import math
class QModelWidget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(QModelWidget, self).__init__(parent = parent)
        nagi_cpp.LAppDelegate.GetInstance().model_init(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def initializeGL(self):
        nagi_cpp.LAppDelegate.GetInstance().model_init(self)
 
    def paintGL(self):
        nagi_cpp.LAppDelegate.GetInstance().update()

    def resizeGL(self, w, h):
        nagi_cpp.LAppDelegate.GetInstance().resize(w, h)
    
    def mouseReleaseEvent(self, event):
        nagi_cpp.LAppDelegate.GetInstance().mouseReleaseEvent(event.x(), event.y())
        return super().mouseReleaseEvent(event)
    
    def mousePressEvent(self, event):
        nagi_cpp.LAppDelegate.GetInstance().mousePressEvent(event.x(), event.y())
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        nagi_cpp.LAppDelegate.GetInstance().mouseMoveEvent(event.x(), event.y())
        return super().mouseMoveEvent(event)
