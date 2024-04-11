from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtGui import QCloseEvent
from src.client.musics_widget import MusicWidget
from src.client.tools_widget import ToolsWidget
from src.client.tools import switch_widgets
from src.client.slider import Slider
import json
from settings import CONFIG_PATH
import peewee


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.__init_ui()
        self.__setting_ui()
        self.show()
        # switch_widgets(widgets=self.__dict__, switch=False)
    
    def __init_ui(self) -> None:
        self.central_widget = QtWidgets.QWidget()
        self.main_v_layout = QtWidgets.QVBoxLayout()
        self.tool_bar = QtWidgets.QToolBar(self)
        self.open_file_dialog_action = QtGui.QAction('Open', self)
        self.clear_music_list_action = QtGui.QAction('Clear', self)
        self.randomize_musics_action = QtGui.QAction('Shuffle', self)
        self.music_widget = MusicWidget(self)
        self.tools_widget = ToolsWidget(self)
    
    def __setting_ui(self) -> None:
        self.setWindowTitle('Shesterochka Player')
        self.resize(550, 440)
        self.setCentralWidget(self.central_widget)
        self.addToolBar(self.tool_bar)
        self.tool_bar.addAction(self.open_file_dialog_action)
        self.tool_bar.addAction(self.randomize_musics_action)
        self.tool_bar.addAction(self.clear_music_list_action)
        self.central_widget.setLayout(self.main_v_layout)
        self.main_v_layout.setContentsMargins(0,0,0,0)
        self.main_v_layout.addWidget(self.music_widget)
        self.main_v_layout.addWidget(self.tools_widget)

        self.music_widget.table.mousePressEvent = lambda event: self.modifyMousePressEvent(event=event, widget=self.music_widget.table, parent=QtWidgets.QTableWidget)
        self.tools_widget.audio_time_widget.slider.mousePressEvent = lambda event: self.modifyMousePressEvent(event, widget=self.tools_widget.audio_time_widget.slider, parent=Slider)
        
        if self.music_widget.table.rowCount() == 0:
            self.tools_widget.switch_buttons(False)

        self.show()

        self.tools_widget.volume_dialog.show()
        self.tools_widget.volume_dialog.move(self.tools_widget.volume_button.mapToGlobal(QtCore.QPoint(-11, -72)))
        self.tools_widget.volume_dialog.hide()

        self.hide()

        self.open_file_dialog_action.triggered.connect(self.open_action_clicked)
        self.clear_music_list_action.triggered.connect(self.clear_action_clicked)
        self.randomize_musics_action.triggered.connect(self.randomize_action_clicked)

    def show_message(self, text: str, error: bool = False, parent: QtWidgets.QWidget = None):
        message_box = QtWidgets.QMessageBox(parent=self if not parent else parent)
        message_box.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        message_box.setWindowTitle('Error' if error else 'Information')
        message_box.setIcon(QtWidgets.QMessageBox.Icon.Critical if error else QtWidgets.QMessageBox.Icon.Information)
        message_box.setText(text)
        message_box.exec_()

    def modifyMousePressEvent(self, event: QtGui.QMouseEvent, parent: QtWidgets.QWidget, widget: QtWidgets.QWidget) -> None:
        self.mousePressEvent(event)
        parent.mousePressEvent(widget, event)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.tools_widget.volume_dialog:
            self.tools_widget.volume_dialog.hide()
        return super().mousePressEvent(event)
    
    def moveEvent(self, event: QtGui.QMoveEvent) -> None:
        if self.tools_widget:
            self.tools_widget.volume_dialog.move(self.tools_widget.volume_button.mapToGlobal(QtCore.QPoint(-11, -72)))
            
        return super().moveEvent(event)

    def open_action_clicked(self) -> None:
        loaded_files, names_files, path_to_files = self.music_widget.get_files_for_fill([QtCore.QFileInfo(elem) for elem in QtWidgets.QFileDialog().getOpenFileNames(self, 'Open files', filter='Music (*.mp3; *.wav; *.opus;)')[0]])
        self.music_widget.update_musics(loaded_files, names_files, path_to_files)
        self.tools_widget.switch_buttons(True)
        
    def clear_action_clicked(self) -> None:
        self.music_widget.stop_flag = True
        try:
            self.music_widget.clear_musics()
        except peewee.OperationalError:
            self.music_widget.clear_musics()

        self.tools_widget.switch_buttons(False)
        self.music_widget.stop_flag = False


    def randomize_action_clicked(self) -> None:
        self.music_widget.randomize()

    def closeEvent(self, event: QCloseEvent) -> None:
        
        with open(CONFIG_PATH, 'w') as file:
            json.dump({'volume': self.tools_widget.volume_dialog.volume_slider.value()}, file)

        self.tools_widget.audio_player.stop()   
        self.music_widget.stop_flag = True
        exit()