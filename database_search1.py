from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QWidget
from literature_ui import Ui_QtLiterature
from extra_param_ui import Ui_Form
import sqlite3
from global_parameters import SEARCH_HAS_EXTRA_PARAMETERS, SQL_EXECUTION, EXTRA_PARAM, FILE_DB_NAME
from book_reader import *


class SearchError(Exception):
    """
        Ошибка поиска
    """
    pass


class BookNotFound(SearchError):
    """
        Книга не найдена
    """
    pass


class SearchParameters(QMainWindow, Ui_QtLiterature):
    """
        Инициализация БД
    """
    def __init__(self, visual_ui_class):
        super().__init__()
        self.visual_ui = visual_ui_class
        self.connection_db = sqlite3.connect(FILE_DB_NAME)
        self.cursor = self.connection_db.cursor()
        books = self.cursor.execute('''select books.title, genres.title, authors.title
                 from books left join genres on books.genreId = genres.id 
                 join authors on books.authorId = authors.id''').fetchall()
        self.load_table(books)
        self.visual_ui.searchButton.clicked.connect(self.search)
        self.visual_ui.extraParamButton.clicked.connect(self.show_extra_param)
        self.visual_ui.showFavouriteButton.clicked.connect(self.show_favourites)

    """
        Загрузка таблицы в QTableWidget
    """
    def load_table(self, books):
        self.visual_ui.databaseWidget.setColumnCount(3)
        self.visual_ui.databaseWidget.setRowCount(0)

        self.visual_ui.databaseWidget.setHorizontalHeaderLabels(['Название', 'Жанр', 'Автор'])
        for i, row in enumerate(books):
            self.visual_ui.databaseWidget.setRowCount(
                self.visual_ui.databaseWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.visual_ui.databaseWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))
        self.visual_ui.databaseWidget.resizeColumnsToContents()

    """
        Метод поиска по названию, автору или жанру
    """
    def search(self):
        global SEARCH_HAS_EXTRA_PARAMETERS, SQL_EXECUTION
        try:
            if SEARCH_HAS_EXTRA_PARAMETERS:
                if self.visual_ui.searchLine.text() == '':
                    if 'and books.title' in SQL_EXECUTION[-1] or 'where books.title' in SQL_EXECUTION[-1]:
                        SQL_EXECUTION = SQL_EXECUTION[0]
                    result = self.cursor.execute(SQL_EXECUTION).fetchall()
                    if result:
                        self.load_table(result)
                    else:
                        raise BookNotFound
                else:
                    if len(SQL_EXECUTION) != 2:
                        if SQL_EXECUTION[-1].endswith("'"):
                            SQL_EXECUTION = [SQL_EXECUTION, f" and books.title"
                                                            f" like '%{self.visual_ui.searchLine.text()}%'"]
                        else:
                            SQL_EXECUTION = [SQL_EXECUTION, f" where books.title"
                                                            f" like '%{self.visual_ui.searchLine.text()}%'"]
                    else:
                        if SQL_EXECUTION[-1] != self.searchLine.text():
                            SQL_EXECUTION = [SQL_EXECUTION[0], f" and books.title like"
                                                               f" '%{self.visual_ui.searchLine.text()}%'"]
                    result = self.cursor.execute(''.join(SQL_EXECUTION)).fetchall()
                    if result:
                        self.load_table(result)
                    else:
                        raise BookNotFound
            else:
                if self.visual_ui.searchLine.text() == '':
                    result = self.cursor.execute('''select books.title, genres.title, authors.title
                                     from books left join genres on books.genreId = genres.id 
                                     join authors on books.authorId = authors.id''').fetchall()
                    self.load_table(result)
                else:
                    search_text = self.visual_ui.searchLine.text()
                    result = self.cursor.execute(f"""select books.title, genres.title, authors.title
                         from books left join genres on books.genreId = genres.id 
                         join authors on books.authorId = authors.id
                          where books.title like '%{search_text}%'""").fetchall()
                    if result:
                        self.load_table(result)
                    else:
                        raise BookNotFound
        except BookNotFound:
            self.visual_ui.popup.setText('НИЧЕГО НЕ НАЙДЕНО')
            self.visual_ui.popup_class.posx = 15
            self.visual_ui.popup_class.posy = 46
            self.visual_ui.popup_class.show()

    """
        Показать окно поиска с доп. параметрами
    """
    def show_extra_param(self):
        self.window2 = SearchExtraParameters()
        self.visual_ui.set_style_another(self.window2)

    """
        Показать избранные
    """
    def show_favourites(self):
        favourite_books = self.cursor.execute("""select books.title, genres.title, authors.title
                         from books left join genres on books.genreId = genres.id 
                         join authors on books.authorId = authors.id where isFavourite = 1""").fetchall()
        if favourite_books:
            self.load_table(favourite_books)
        else:
            self.visual_ui.popup.setText('У ВАС НЕТ ИЗБР. КНИГ')
            self.visual_ui.popup_class.posx = 15
            self.visual_ui.popup_class.posy = 46
            self.visual_ui.popup_class.show()


class SearchExtraParameters(QWidget, Ui_Form):
    """
        Окно поиска книг из БД с доп. параметрами
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.saveButton.clicked.connect(self.give_to_search)
        file_name = 'literature_db.db'
        self.connection_db = sqlite3.connect(file_name)
        self.cursor = self.connection_db.cursor()
        genres = self.cursor.execute('''select title from genres''').fetchall()
        self.cboxGenre.addItem('Все')
        for i in genres:
            self.cboxGenre.addItem(i[0])
        self.load_saved_sql()
        self.resetButton.clicked.connect(self.reset_values)

    """
        Создание Sql-запроса доп.параметров
    """
    def give_to_search(self):
        global SQL_EXECUTION, SEARCH_HAS_EXTRA_PARAMETERS, EXTRA_PARAM
        EXTRA_PARAM = []
        SQL_EXECUTION = '''select books.title, genres.title, authors.title
                 from books left join genres on books.genreId = genres.id 
                 join authors on books.authorId = authors.id'''

        EXTRA_PARAM.append(self.cboxGenre.currentText())
        if self.cboxGenre.currentText() != '':
            if EXTRA_PARAM[0] == 'Все':
                pass
            elif SQL_EXECUTION.endswith("'"):
                SQL_EXECUTION += f""" and genres.title = '{EXTRA_PARAM[-1]}'"""
            else:
                SQL_EXECUTION += f""" where genres.title = '{EXTRA_PARAM[-1]}'"""
        EXTRA_PARAM.append(self.authorTitle.text())
        if self.authorTitle.text() != '':
            if SQL_EXECUTION.endswith("'"):
                SQL_EXECUTION += f""" and authors.title = '{EXTRA_PARAM[-1]}'"""
            else:
                SQL_EXECUTION += f""" where authors.title = '{EXTRA_PARAM[-1]}'"""
        SEARCH_HAS_EXTRA_PARAMETERS = True
        self.close_window()

    """
        Загрузка sql-запроса обратно в lineEdit и comboBox
    """
    def load_saved_sql(self):
        global EXTRA_PARAM
        if EXTRA_PARAM[0] != '' and EXTRA_PARAM[0] != 'Все':
            genre_id = self.cursor.execute(f"""select id from genres where title = 
                '{EXTRA_PARAM[0]}'""").fetchone()[0]
            self.cboxGenre.setCurrentIndex(int(genre_id))
        else:
            self.cboxGenre.setCurrentIndex(0)
        self.authorTitle.setText(EXTRA_PARAM[-1])

    """
        Сброс значений в lineEdit и comboBox
    """
    def reset_values(self):
        global EXTRA_PARAM, SEARCH_HAS_EXTRA_PARAMETERS
        EXTRA_PARAM = ['', '']
        self.cboxGenre.setCurrentIndex(0)
        self.authorTitle.setText('')
        SEARCH_HAS_EXTRA_PARAMETERS = False

    """
        Метод закрытия окна
    """
    def close_window(self):
        self.close()
