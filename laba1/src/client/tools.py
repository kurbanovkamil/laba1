from PySide6 import QtGui, QtWidgets, QtCore
import settings


def get_pixmap(name: str) -> None:
    return QtGui.QPixmap(f'{settings.IMG_DIR}/{name}.png')


def switch_widgets(widgets: dict[QtWidgets.QWidget], switch: bool):
    for key, widget in widgets.items():
        if isinstance(widget, QtWidgets.QWidget):
            widget.show() if switch else widget.hide()