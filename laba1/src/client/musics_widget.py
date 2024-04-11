from PySide6 import QtWidgets, QtCore, QtGui
from src.database.database_models import Musics
import random
import enum
import peewee
import tinytag
import threading
import time


class TypesData(enum.Enum):
    ImgRole: int = 1001



class MusicWidget(QtWidgets.QWidget):
    flag: int = 0
    row: int = 0
    stop_flag: bool = False
    add_music_signal = QtCore.Signal(str, str, str)
    show_message_signal = QtCore.Signal(str, bool)
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent=parent)
        self.parent = parent
        self.__init_ui()
        self.__setting_ui()
    
    def __init_ui(self) -> None:
        self.main_h_layout = QtWidgets.QHBoxLayout()
        self.table = QtWidgets.QTableWidget()
        self.tools_v_layout = QtWidgets.QVBoxLayout()

    def __setting_ui(self) -> None:
        self.setLayout(self.main_h_layout)
        self.main_h_layout.addWidget(self.table)
        self.main_h_layout.addLayout(self.tools_v_layout)
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setColumnHidden(2, True)
        
        self.tools_v_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.table.setHorizontalHeaderLabels(["Исполнитель", "Имя песни"])

        self.table.cellClicked.connect(self.click_cell)
        self.table.currentItemChanged.connect(self.current_item_changed)

        self.add_music_signal.connect(self.add_music)
        self.show_message_signal.connect(self.show_message)
 
        threading.Thread(target=self.fill_musics).start()
    
    def click_cell(self) -> None:
        if not self.parent.tools_widget.audio_player.hasAudio():
            self.parent.tools_widget.current_music_path = self.table.model().index(self.table.currentRow(), 2).data()
        
        if self.parent.tools_widget.audio_player.isPlaying():
            self.parent.tools_widget.pause()
            return
        
        self.parent.tools_widget.play()

    def current_item_changed(self, _: QtWidgets.QTableWidgetItem, __: QtWidgets.QTableWidgetItem) -> None:
        if not self.parent.tools_widget.audio_player.hasAudio():
            self.parent.tools_widget.current_music_path = self.table.model().index(self.table.currentRow(), 2).data()
            return
        self.parent.tools_widget.new_music_path = self.table.model().index(self.table.currentRow(), 2).data()
    
    def shuffle_items(self) -> list:
        indexes = [(row, column) for row in range(self.table.rowCount()) for column in range(self.table.columnCount())]
        result = [indexes[i:i+self.table.columnCount()] for i in range(0, len(indexes), self.table.columnCount())]
        random.shuffle(result)
        return result

    def randomize(self) -> None:
        new_rows = random.sample(range(0, self.table.rowCount()), self.table.rowCount())
        for row, new_row in zip(self.shuffle_items(), new_rows):
            for attr in row:
                old_row = attr[0]
                old_column = attr[1]
                old_item = self.table.takeItem(old_row, old_column)
                new_column = attr[1]
                new_item = self.table.takeItem(new_row, new_column)
                self.table.setItem(old_row, old_column, new_item)
                self.table.setItem(new_row, new_column, old_item)

    def get_files_for_fill(self, list_files: list[QtCore.QFileInfo]) -> tuple[str]:
        path_to_files = [str(elem.absoluteFilePath()) for elem in list_files]
        names_files = [str(elem.fileName()) for elem in list_files]
        loaded_files = [tinytag.TinyTag.get(file) for file in path_to_files]
        return loaded_files, names_files, path_to_files
    
    def update_musics(self, loaded_files: list[tinytag.TinyTag], names_files: list[str], path_to_files: list[str]) -> None:
        new_thread = threading.Thread(target=self.fill_database, args=(loaded_files, names_files, path_to_files))
        new_thread.start()

    def show_message(self, text, error) -> None:
        self.parent.show_message(text, error)

    def fill_database(self, loaded_files: list[tinytag.TinyTag], names_files: list[str], path_to_files: list[str]):
        self.list_not_unique_music = [] 
        for item, name, path in zip(loaded_files, names_files, path_to_files):
            if self.stop_flag:  
                exit()
                
            try:
                item.artist = 'Unknown' if not item.artist else item.artist
                item.title = name.split('.')[0] if not item.title else item.title

                Musics.create(artist=item.artist,
                              title=item.title, 
                              path=path)      

                self.add_music_signal.emit(
                    item.artist,
                    item.title,
                    path
                )

                time.sleep(0.015)

            except peewee.IntegrityError: 
                self.list_not_unique_music.append(f'{item.artist} - {item.title}')
        
        if len(self.list_not_unique_music) > 0:
            self.show_message_signal.emit(
                f'This musics are uploaded: {str(self.list_not_unique_music).replace("[", "").replace("]", "")}',
                True
            )
            self.list_not_unique_music.clear()
        
        self.table.setCurrentCell(0, 0)

    def fill_musics(self, musics=Musics.select()) -> None:  
        for model in musics:
            if self.stop_flag:  
                exit()

            self.add_music_signal.emit(
                model.artist,
                model.title,
                model.path
            )

            time.sleep(0.03)

    QtCore.Slot(str, str, str)
    def add_music(self, artist: str, title: str, path: str) -> None:
        for index, item in enumerate([artist, title, path]): 
            itemWidget = QtWidgets.QTableWidgetItem(item)
            self.table.setRowCount(self.row + 1)
            self.table.setItem(self.row, index, itemWidget)
        self.row += 1     

    def clear_database(self) -> None:
        for model in Musics.select():
            model.delete().execute()

    def clear_musics(self) -> None:
        self.parent.tools_widget.current_music_path, \
        self.parent.tools_widget.new_music_path = None, None
        self.parent.tools_widget.stop()
        self.clear_database()
        self.table.clearContents()
        self.table.setRowCount(0)
        self.row = 0

