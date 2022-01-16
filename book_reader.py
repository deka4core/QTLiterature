from PyQt5.QtCore import QPropertyAnimation, QPoint, QSize, QEasingCurve, QParallelAnimationGroup
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QGraphicsOpacityEffect
from literature_ui import Ui_QtLiterature
import sqlite3
import pathlib
from global_parameters import FILE_DB_NAME, BOOK_OPENED_PATH, CURRENT_BOOK, CURRENT_PAGE, BOOKMARKS
from PyQt5 import QtCore


class ReaderError(Exception):
    """
        Ошибка читалки
    """
    pass


class BookNotSelected(ReaderError):
    """
        Книга не выбрана
    """
    pass


class TextNotFound(ReaderError):
    """
        Текст не найден (совсем)
    """
    pass


class TextNotFoundBelow(ReaderError):
    """
        Текст не найден ниже
    """
    pass


class Reader:
    """
        Инициализация читалки
    """
    def __init__(self, visual_ui_class):
        self.visual_ui = visual_ui_class
        self.connection_db = sqlite3.connect(FILE_DB_NAME)
        self.cursor = self.connection_db.cursor()
        self.visual_ui.openBookButton.clicked.connect(self.selectItems)
        self.visual_ui.openBookButton.clicked.connect(self.check_bookmark)
        self.visual_ui.nextPageButton.clicked.connect(self.turn_page_forward)
        self.visual_ui.nextPageButton.clicked.connect(self.check_bookmark)
        self.visual_ui.previousPageButton.clicked.connect(self.turn_page_backward)
        self.visual_ui.previousPageButton.clicked.connect(self.check_bookmark)
        self.visual_ui.setBookmarkButton.clicked.connect(self.add_bookmark)
        self.visual_ui.goToMarkButton.clicked.connect(self.go_to_bookmark)
        self.visual_ui.addToFavouriteButton.clicked.connect(self.add_to_favourites)

    """
        Выбранный предмет в БД открыть в PlainText
    """
    def selectItems(self):
        global BOOK_OPENED_PATH, CURRENT_PAGE, CURRENT_BOOK
        CURRENT_BOOK = []
        CURRENT_PAGE = 0
        index = self.visual_ui.databaseWidget.currentRow()
        try:
            if index > -1:
                cell = self.visual_ui.databaseWidget.item(index, 0).text()
                path_to_book = self.cursor.execute(f"""select * from books where title = '{cell}'""").fetchone()[-2]
                path_to_book = path_to_book.replace('"', '')
                BOOK_OPENED_PATH = path_to_book
                with open(path_to_book, 'r', encoding='utf8') as book_file:
                    chunk = book_file.read(2000)
                    while chunk:
                        CURRENT_BOOK.append(chunk)
                        chunk = book_file.read(2000)
                    self.visual_ui.bookReaderWidget.setPlainText(CURRENT_BOOK[CURRENT_PAGE])
            else:
                raise BookNotSelected
        except BookNotSelected:
            self.visual_ui.popup.setText('КНИГА НЕ ВЫБРАНА')
            self.visual_ui.popup_class.posx = self.visual_ui.size().width() - 215
            self.visual_ui.popup_class.show()

    """
        Перевернуть страницу на следующую
    """
    def turn_page_forward(self):
        global CURRENT_PAGE, CURRENT_BOOK
        if CURRENT_BOOK:
            CURRENT_PAGE += 1
            self.visual_ui.bookReaderWidget.setPlainText(CURRENT_BOOK[CURRENT_PAGE])

    """
        Перевернуть страницу на предыдущую
    """
    def turn_page_backward(self):
        global CURRENT_PAGE, CURRENT_BOOK
        if CURRENT_BOOK:
            CURRENT_PAGE -= 1 if CURRENT_PAGE != 0 else 0
            self.visual_ui.bookReaderWidget.setPlainText(CURRENT_BOOK[CURRENT_PAGE])

    """
        Добавить закладку
    """
    def add_bookmark(self):
        global CURRENT_BOOK, CURRENT_PAGE, BOOKMARKS
        if CURRENT_BOOK:
            if CURRENT_BOOK[0] not in BOOKMARKS:
                BOOKMARKS[CURRENT_BOOK[0]] = CURRENT_PAGE
                self.check_bookmark()
            else:
                if BOOKMARKS[CURRENT_BOOK[0]] == CURRENT_PAGE:
                    del BOOKMARKS[CURRENT_BOOK[0]]
                    self.check_bookmark()
                else:
                    BOOKMARKS[CURRENT_BOOK[0]] = CURRENT_PAGE
                    self.check_bookmark()

    """
        Проверка закладки на странице
    """
    def check_bookmark(self):
        global CURRENT_BOOK, CURRENT_PAGE, BOOKMARKS
        if CURRENT_BOOK:
            if CURRENT_BOOK[0] in BOOKMARKS:
                if CURRENT_PAGE == BOOKMARKS[CURRENT_BOOK[0]]:
                    self.visual_ui.bookmark_class.show()
                else:
                    self.visual_ui.bookmark_class.hide()
            else:
                self.visual_ui.bookmark_class.hide()

    """
        Переместиться к закладке
    """
    def go_to_bookmark(self):
        global CURRENT_BOOK, BOOKMARKS, CURRENT_PAGE
        if CURRENT_BOOK:
            if CURRENT_BOOK[0] in BOOKMARKS:
                CURRENT_PAGE = BOOKMARKS[CURRENT_BOOK[0]]
                self.visual_ui.bookReaderWidget.setPlainText(str(CURRENT_BOOK[CURRENT_PAGE]))
                self.check_bookmark()

    """
        Добавить в избранное
    """
    def add_to_favourites(self):
        global BOOK_OPENED_PATH
        is_favourites = self.cursor.execute(f"""select isFavourite from books
         where path = '"{BOOK_OPENED_PATH}"'""").fetchone()[0]
        if is_favourites != 1:
            self.cursor.execute(f"""update books set isFavourite = 1 where path = '"{BOOK_OPENED_PATH}"'""")
            self.connection_db.commit()
            self.visual_ui.popup.setText('КНИГА ДОБАВЛЕНА В ИЗБР.')
            self.visual_ui.popup_class.posx = self.visual_ui.size().width() - 215
            self.visual_ui.popup_class.show()
        else:
            self.cursor.execute(f"""update books set isFavourite = 0 where path = '"{BOOK_OPENED_PATH}"'""")
            self.connection_db.commit()
            self.visual_ui.popup.setText('КНИГА УДАЛЕНА ИЗ ИЗБР.')
            self.visual_ui.popup_class.posx = self.visual_ui.size().width() - 215
            self.visual_ui.popup_class.show()


class BookMark:
    """
        Инициализация закладки
    """
    def __init__(self, visual_ui_class):
        self.visual_ui_class = visual_ui_class
        self.bookmark_size = QSize(23, 100)
        self.opacity_end = 0.4
        self.animation_duration = 1500
        self.visual_ui_class.resized.connect(self.init_bookmarks)
        self.init_bookmark_button()
        self.visual_ui_class.bookmark.setVisible(False)

    """
        Показать закладку
    """
    def show(self):
        self.visual_ui_class.bookmark.setVisible(True)
        self.bookmark_size = QSize(23, 100)
        self.opacity_end = 0.4
        self.animation_duration = 1500
        self.init_bookmarks()
        self.init_animation()

    """
        Спрятать закладку
    """
    def hide(self):
        self.visual_ui_class.bookmark.setVisible(False)

    """
        Инициализация интерфейса и позиции закладки
    """
    def init_bookmarks(self):
        self.visual_ui_class.bookmark.move(self.visual_ui_class.bookReaderWidget.size().width() - 23 * 2, -2)
        self.visual_ui_class.bookmark.resize(self.bookmark_size)
        self.visual_ui_class.bookmark.setStyleSheet("""border-image: url(img/bookmark.png);""")

    """
        Инициализация анимации закладки
    """
    def init_animation(self):
        effect = QGraphicsOpacityEffect(self.visual_ui_class.bookmark)
        self.bookmark_size = QSize(23, 40)
        self.visual_ui_class.bookmark.setGraphicsEffect(effect)
        self.animation = QPropertyAnimation(self.visual_ui_class.bookmark, b"size")
        self.animation_opacity = QPropertyAnimation(effect, b"opacity")
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.setEndValue(self.bookmark_size)
        self.animation.setDuration(self.animation_duration)
        self.animation.start()
        self.animation_opacity.setStartValue(1)
        self.animation_opacity.setEndValue(self.opacity_end)
        self.animation_opacity.setDuration(self.animation_duration)
        self.animation_opacity.setEasingCurve(QEasingCurve.InExpo)
        self.animation_opacity.start()

    """
        Инициализация стилей кнопок закладки
    """
    def init_bookmark_button(self):
        icon = QIcon('img/bookmark_add_ico.png')
        self.visual_ui_class.setBookmarkButton.setIcon(icon)
        icon = QIcon('img/bookmark_ico.png')
        self.visual_ui_class.goToMarkButton.setIcon(icon)


class TextSizeSlider:
    def __init__(self, visual_ui):
        self.visual_ui = visual_ui
        self.visual_ui.textSizeSlider.valueChanged.connect(self.change)

    def change(self):
        self.visual_ui.textSizeLabel.setText('Размер шрифта: ' + str(self.visual_ui.textSizeSlider.value()))
        self.visual_ui.bookReaderWidget.setStyleSheet(f'font-size: {self.visual_ui.textSizeSlider.value()}px;')