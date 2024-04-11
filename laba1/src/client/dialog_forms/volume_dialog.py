from PySide6 import QtWidgets, QtCore, QtGui
from src.client.slider import Slider


class VolumeSliderDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.__init_ui()
        self.__setting_ui()
    
    def __init_ui(self) -> None:
        self.main_h_layout = QtWidgets.QHBoxLayout()
        self.volume_slider = Slider(self, QtCore.Qt.Orientation.Vertical, style="""
            QSlider::handle:vertical {
                width: 3px; /* Ширина ползунка */
                height: 3px; /* Высота ползунка */
                margin: -3px 0; /* Выравнивание ползунка */
                background: #000000; /* Цвет ползунка */
                border-radius: 2px; /* Скругление углов ползунка */
            }

            QSlider::groove:vertical {
                height: 35px; /* Высота "борозды" ползунка */
                background: #808080; /* Цвет "борозды" ползунка */
                border-radius: 3px; /* Скругление углов "борозды" ползунка */
            }
        """)
    
    def __setting_ui(self) -> None:
        self.setLayout(self.main_h_layout)
        self.setWindowFlags(QtCore.Qt.WindowType.CoverWindow | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setFixedHeight(65)
        self.setFixedWidth(45)
        self.main_h_layout.addWidget(self.volume_slider)