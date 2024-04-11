from PySide6 import QtWidgets, QtCore, QtGui


class Slider(QtWidgets.QSlider):
    current_slide_seconds = 0
    mouse_pressed = False
    def __init__(self, parent, orientation: QtCore.Qt.Orientation, style: str) -> None:
        super().__init__(parent)
        self.parent = parent
        self.__setting_ui(orientation, style)
    
    def __setting_ui(self, orientation: QtCore.Qt.Orientation, style: str) -> None:
        self.setValue(0)
        self.setMinimum(0)
        self.setMaximum(100)
        self.installEventFilter(self)
        self.setOrientation(orientation)
        self.setStyleSheet(style)

    def get_new_value(self, event) -> int:
        return self.maximum() - \
            (event.y() / self.height()) * \
            (self.maximum() - self.minimum()) \
            if self.orientation() == QtCore.Qt.Orientation.Vertical else \
                self.minimum() + \
                        (event.x() / self.width()) * \
                        (self.maximum() - self.minimum())

    def wheelEvent(self, event):
        event.ignore()

    def mousePressEvent(self, event):
        self.mouse_pressed = True

        new_value = self.get_new_value(event)
        
        self.setValue(int(new_value))

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            new_value = self.get_new_value(event)
            
            self.setValue(int(new_value))

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False