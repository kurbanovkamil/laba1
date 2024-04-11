from PySide6 import QtWidgets, QtCore, QtGui, QtMultimedia
from PySide6.QtWidgets import QWidget
from src.client.audio_timer_widget import AudioTimeWidget
import time
from src.client.dialog_forms.volume_dialog import VolumeSliderDialog
from src.client.tools import get_pixmap
import json
from settings import CONFIG_PATH

class ToolsWidget(QtWidgets.QWidget):
    audio_device_changed_signal = QtCore.Signal(QtMultimedia.QAudioDevice,)
    stop_flag: bool = False
    index_row = -1
    new_music_path: str = None
    current_music_path: str = None
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.parent = parent
        self.__init_ui()
        self.__setting_ui()

    def __init_ui(self) -> None:
        self.main_v_layout = QtWidgets.QVBoxLayout()
        self.buttons_h_layout = QtWidgets.QHBoxLayout()
        self.audio_player = QtMultimedia.QMediaPlayer(self)
        self.audio_output = QtMultimedia.QAudioOutput()
        self.determine_audio_output_timer = QtCore.QTimer(self)
        self.audio_time_widget = AudioTimeWidget(self)
        self.listen_button = QtWidgets.QToolButton()
        self.pause_button = QtWidgets.QToolButton()
        self.stop_button = QtWidgets.QToolButton()
        self.next_button = QtWidgets.QToolButton()
        self.previous_button = QtWidgets.QToolButton()
        self.volume_button = QtWidgets.QToolButton()
        self.volume_dialog = VolumeSliderDialog(self)

    def __setting_ui(self) -> None:
        self.setLayout(self.main_v_layout)

        self.audio_player.setAudioOutput(self.audio_output)

        self.main_v_layout.addLayout(self.buttons_h_layout)
        self.buttons_h_layout.addWidget(self.previous_button)
        self.buttons_h_layout.addWidget(self.listen_button)
        self.buttons_h_layout.addWidget(self.pause_button)
        self.buttons_h_layout.addWidget(self.stop_button)
        self.buttons_h_layout.addWidget(self.next_button)
        self.buttons_h_layout.addWidget(self.audio_time_widget)
        self.buttons_h_layout.addWidget(self.volume_button)
        
        self.listen_button.setIcon(get_pixmap('play'))
        self.pause_button.setIcon(get_pixmap('pause'))
        self.stop_button.setIcon(get_pixmap('stop'))
        self.next_button.setIcon(get_pixmap('next'))
        self.previous_button.setIcon(get_pixmap('previous'))
        self.volume_button.setIcon(get_pixmap('volume'))

        self.volume_dialog.volume_slider.setValue(self.get_volume())
        self.change_volume_value(None)
    
        self.previous_button.clicked.connect(self.previous_audio_button_click)
        self.listen_button.clicked.connect(self.play)
        self.pause_button.clicked.connect(self.pause)
        self.stop_button.clicked.connect(self.stop)
        self.next_button.clicked.connect(self.next_audio_button_click)
        self.volume_button.clicked.connect(self.on_volume_button_click)
        self.audio_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.audio_device_changed_signal.connect(self.change_audio_output)
        self.volume_dialog.volume_slider.valueChanged.connect(self.change_volume_value)
        self.determine_audio_output_timer.timeout.connect(self.determine_audio_output)
        self.determine_audio_output_timer.start(500)

    def get_volume(self) -> int:
        with open(CONFIG_PATH, 'r') as file:
            data = json.load(file)['volume']
        
        return data

    def change_audio_output(self, audio_device: QtMultimedia.QAudioDevice) -> None:
        self.audio_output = QtMultimedia.QAudioOutput(audio_device)
        self.audio_player.setAudioOutput(self.audio_output)
        self.volume_dialog.volume_slider.setValue(self.get_volume())

    def determine_audio_output(self) -> None:
        devices = QtMultimedia.QMediaDevices().audioOutputs()
        for device in devices:
            if self.audio_output.device() != device and 'Наушники' in device.description() :
                self.audio_device_changed_signal.emit(device)

        if self.audio_output.device() not in devices:
            self.audio_device_changed_signal.emit(devices[0])
    
    def on_media_status_changed(self, status: QtMultimedia.QMediaPlayer.MediaStatus):
        if status == QtMultimedia.QMediaPlayer.MediaStatus.EndOfMedia:
            self.next_audio_button_click()
    
    def change_volume_value(self, event) -> None:
        self.audio_output.setVolume(float(self.volume_dialog.volume_slider.value()) / 100)
    
    def on_volume_button_click(self) -> None:
        if self.volume_dialog.isVisible():
            self.volume_dialog.hide()
            return
       
        self.volume_dialog.show()

    def pause(self) -> None:
        self.audio_player.pause()

    def play(self) -> None:
        print(self.current_music_path, self.new_music_path)
        if not self.audio_player.hasAudio():
            self.set_audio(self.current_music_path)
            self.start_timers()

        if self.current_music_path != self.new_music_path and self.new_music_path:
            self.current_music_path = self.new_music_path
            self.stop_button.click()
            time.sleep(0.01)
            self.set_audio(self.current_music_path)

        self.audio_player.play()

    def stop_timers(self) -> None:
        self.audio_time_widget.calculate_timer.stop()
        self.audio_time_widget.update_timer.stop()

    def start_timers(self) -> None:
        self.audio_time_widget.calculate_timer.start(200)
        self.audio_time_widget.update_timer.start(300)

    def switch_buttons(self, switch: bool) -> None:
        self.listen_button.setEnabled(switch)
        self.stop_button.setEnabled(switch)
        self.pause_button.setEnabled(switch)
        self.next_button.setEnabled(switch)
        self.previous_button.setEnabled(switch)  

    def next_audio_button_click(self) -> None:
        self.index_row = (self.parent.music_widget.table.currentRow() + 1) if self.parent.music_widget.table.currentRow() < self.parent.music_widget.table.rowCount() - 1 else 0

        self.parent.music_widget.table.setCurrentCell(self.index_row, 1)

        self.play()

    def previous_audio_button_click(self) -> None:
        self.index_row = (self.parent.music_widget.table.currentRow() - 1) if self.parent.music_widget.table.currentRow() > 0 else self.parent.music_widget.table.rowCount() - 1

        self.parent.music_widget.table.setCurrentCell(self.index_row, 1)

        self.play()

    def stop(self) -> None:
        self.audio_player.stop()

    def set_audio(self, music_path: str):
        print(music_path)
        self.audio_player.setSource(QtCore.QUrl().fromLocalFile(music_path))