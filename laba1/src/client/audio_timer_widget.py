from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6 import QtGui, QtCore
from src.client.slider import Slider
from PySide6.QtWidgets import QApplication, QWidget, QSlider, QVBoxLayout
from PySide6.QtCore import Qt, QPoint
import time

class AudioTimeWidget(QWidget):
    stop_flag: bool = False
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.__init_ui()
        self.__setup_ui()


    def __init_ui(self) -> None:
        self.main_h_layout = QHBoxLayout()
        self.current_time_label = QLabel(text='0:00')
        self.total_time_label = QLabel(text='0:00')
        self.slider = Slider(parent=self, orientation=QtCore.Qt.Orientation.Horizontal, style="""
            QSlider::handle:horizontal {
                width: 5px; /* Ширина ползунка */
                height: 6px; /* Высота ползунка */
                margin: -3px 0; /* Выравнивание ползунка */
                background: #000000; /* Цвет ползунка */
                border-radius: 2px; /* Скругление углов ползунка */
            }

            QSlider::groove:horizontal {
                height: 10px; /* Высота "борозды" ползунка */
                background: #808080; /* Цвет "борозды" ползунка */
                border-radius: 3px; /* Скругление углов "борозды" ползунка */
            }
        """)
        self.calculate_timer = QTimer(self)
        self.update_timer = QTimer(self)

    def __setup_ui(self) -> None:
        self.setLayout(self.main_h_layout)

        self.main_h_layout.addWidget(self.current_time_label)
        self.main_h_layout.addWidget(self.slider)
        self.main_h_layout.addWidget(self.total_time_label)

        self.calculate_timer.timeout.connect(self.calculate_time)
        self.update_timer.timeout.connect(self.update_time)
        self.slider.mouseReleaseEvent = self.newMouseReleaseEvent
    
    def get_new_time_code(self) -> None:
        return (int(self.total_time.split(':')[0]) * 60 + int(self.total_time.split(':')[1])) / 100 * self.slider.value()
    
    def set_new_audio_code(self) -> None:
        self.parent.audio_player.setPosition(int(self.get_new_time_code() * 1000))

    def newMouseReleaseEvent(self, event) -> None:
        Slider.mouseReleaseEvent(self.slider, event)
        self.set_new_audio_code()

    def get_current_time(self) -> str:
        return f'{int(self.parent.audio_player.position() / 999.9999999 // 60)}:{int(self.parent.audio_player.position() / 999.9999999 % 60):02d}'
    
    def get_total_time(self) -> str:
        return f'{int(self.parent.audio_player.duration() / 999.9999999 // 60)}:{int(self.parent.audio_player.duration() / 999.9999999 % 60):02d}'
    
    def calculate_time(self) -> None:
        self.total_time = self.get_total_time()
        self.current_time = self.get_current_time()

    def update_time(self) -> None:
        self.total_time_label.setText(self.total_time)
        self.current_time_label.setText(self.current_time)
        if not self.slider.mouse_pressed:
            self.slider.setValue(((self.parent.audio_player.position() / 1000) / (self.parent.audio_player.duration() / 1000) if self.parent.audio_player.duration() > 0 else 1) * 100) 