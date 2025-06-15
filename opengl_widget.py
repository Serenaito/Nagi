from PySide6 import QtWidgets, QtOpenGL
from OpenGL import GL
from PySide6 import QtOpenGLWidgets
from PySide6.QtCore import QTimer
from nagi_native import nagi_cpp
class opengl_widget(QtOpenGLWidgets.QOpenGLWidget):
    def __init__(self, parent=None):
        super(opengl_widget, self).__init__(parent = parent)
        nagi_cpp.model_init(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(33)

    def initializeGL(self):
        nagi_cpp.model_init(self)
 
    def paintGL(self):
        nagi_cpp.model_update()

    def resizeGL(self, w, h):
        nagi_cpp.model_resize(w, h)
 