from PyQt6.QtCore import QByteArray, Qt
from PyQt6 import QtWidgets, QtGui
import sys
import MySQLdb as mdb

conn = mdb.connect('localhost', 'root', '', 'artart')


def get_data():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cinema")
    res = cursor.fetchall()
    return res


def update_rating(cinema_id):
    cursor = conn.cursor()
    cursor.execute("UPDATE cinema SET rating = rating+0.1 WHERE id_cinema = %s", (cinema_id,))
    conn.commit()
    print('Данные обновлены!')


def get_genres():
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM genre")
    genres = cursor.fetchall()
    cursor.close()
    return [genre[0] for genre in genres]


def get_genre_id(genre_name):
    cursor = conn.cursor()
    cursor.execute("SELECT id_genre FROM genre WHERE name = %s", (genre_name,))
    genre_id = cursor.fetchone()
    cursor.close()
    return genre_id[0] if genre_id else None


def get_data_by_genre(genre_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cinema WHERE id_genre = %s", (genre_id,))
    res = cursor.fetchall()
    cursor.close()
    return res


class MainWin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle('Main Window')
        layout = QtWidgets.QVBoxLayout(self)

        # Добавляем метку для заголовка "Голосование"
        label = QtWidgets.QLabel("Голосование !", self)
        font = label.font()
        font.setPointSize(15)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Добавляем метку для вопроса "Выберите жанр"
        label_2 = QtWidgets.QLabel("Выберите жанр", self)
        layout.addWidget(label_2)

        # Добавляем ComboBox с жанрами
        genres = get_genres()
        self.combo_box = QtWidgets.QComboBox(self)
        self.combo_box.addItems(genres)
        layout.addWidget(self.combo_box)
        self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)

        # Создаем виджет для отображения фильмов
        self.movies_widget = QtWidgets.QWidget(self)
        self.movies_layout = QtWidgets.QVBoxLayout(self.movies_widget)
        layout.addWidget(self.movies_widget)

        # Добавляем кнопку "Проголосовать"
        self.vote_button = QtWidgets.QPushButton('Проголосовать', self)
        layout.addWidget(self.vote_button)
        self.vote_button.clicked.connect(self.on_click)

    def on_combobox_changed(self, index):
        genre_name = self.combo_box.currentText()
        genre_id = get_genre_id(genre_name)
        if genre_id is not None:
            # Очищаем виджет с фильмами перед обновлением
            for i in reversed(range(self.movies_layout.count())):
                widget = self.movies_layout.itemAt(i).widget()
                self.movies_layout.removeWidget(widget)
                widget.deleteLater()

            # Получаем фильмы для выбранного жанра
            movies = get_data_by_genre(genre_id)
            for movie in movies:
                img = movie[2]
                qpixmap = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(QByteArray(img)))
                file_path = f"save_img/{movie[0]}.jpg"
                qpixmap.save(file_path, "JPG")

                rad = QtWidgets.QRadioButton(f"{movie[1]}", self)
                rad.setObjectName(str(movie[0]))  # Преобразуем ID к строке
                rad.setStyleSheet(
                    f"QRadioButton::indicator {{width: 100px; height: 100px;}}"
                    f" QRadioButton::indicator::unchecked {{image: url('save_img/{movie[0]}.jpg');}}"
                    f" QRadioButton::indicator::checked {{image: url('gal.png');}}"
                )
                self.movies_layout.addWidget(rad)
                rad.toggled.connect(self.on_toggled)

    def on_toggled(self, checked):
        radio = self.sender()
        if checked:
            self.selected_radio = radio

    def on_click(self):
        if hasattr(self, 'selected_radio'):
            id_cinema = int(self.selected_radio.objectName())  # Преобразуем ID к целому числу
            update_rating(id_cinema)
            print('Фильм:', self.selected_radio.text())

            # Создаем сообщение об успешном голосовании
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText("Ваш голос успешно учтен!")
            msg.exec()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.setText("Фильм не выбран!")
            msg.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec())
