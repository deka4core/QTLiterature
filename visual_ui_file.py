import sys
import pickle
from PyQt5.QtCore import QSize, QSequentialAnimationGroup
from PyQt5.QtGui import QPixmap, QIcon

from database_search1 import *
from PyQt5.QtWidgets import QApplication, QPushButton, QGridLayout, QLabel
from global_parameters import MAIN_IS_OPENED, CSS_FILE_NAME, BOOKMARKS
from book_reader import QtCore
from faq_file import FAQWindow
from database_append import AppendBook


class MyWidgetUi(QMainWindow, Ui_QtLiterature):
    resized = QtCore.pyqtSignal()
    """
        Инициализация окна
    """
    def __init__(self):
        super().__init__()
        global MAIN_IS_OPENED
        self.setupUi(self)
        self.window1 = SearchParameters(self)
        self.bookReaderWindow = Reader(self)
        self.faqWindow = FAQWindow(self)
        self.appendWindow = AppendBook(self)
        if not MAIN_IS_OPENED:
            self.set_style_main()
            MAIN_IS_OPENED = True
        self.changeThemeButton.clicked.connect(self.change_theme)
        self.bookmark = QLabel(self.bookReaderWidget)
        self.bookmark_class = BookMark(self)
        self.popup = QLabel(self)
        self.popup_class = PopUp(self)
        self.text_slider_class = TextSizeSlider(self)

    """
        Установка стилей для основного окна
    """
    def set_style_main(self):
        global CSS_FILE_NAME
        with open(CSS_FILE_NAME, 'r', encoding='utf8') as css:
            self.setStyleSheet(css.read())

    """
        Установка стиля для вторичного окна
    """
    def set_style_another(self, window):
        global CSS_FILE_NAME
        with open(CSS_FILE_NAME, 'r', encoding='utf8') as css:
            window.setStyleSheet(css.read())
            window.show()

    """
        Сменить тему
    """
    def change_theme(self):
        global CSS_FILE_NAME
        CSS_FILE_NAME = 'stylesheet_dark.css' if CSS_FILE_NAME == 'stylesheet_white.css' else 'stylesheet_white.css'
        self.set_style_main()

    """
        Событие изменения окна
    """
    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    """
        Событие закрытия окна
    """
    def closeEvent(self, event):
        global BOOKMARKS
        file = open("bookmarks.bin", 'wb')
        pickle.dump(BOOKMARKS, file)
        event.accept()


class PopUp:
    """
        Инициализация всплывающих уведомлений
    """
    def __init__(self, visual_ui_file):
        self.visual_ui = visual_ui_file
        self.popup_size = QSize(200, 43)
        self.posx = 10
        self.posy = 56
        self.opacity_end = 0
        self.animation_duration = 1500
        self.visual_ui.resized.connect(self.init_popup)
        self.visual_ui.popup.setVisible(False)

    """
        Показать
    """
    def show(self):
        self.visual_ui.popup.setVisible(True)
        self.init_popup()
        self.init_animation()

    """
        Инициализация стилей
    """
    def init_popup(self):
        self.visual_ui.popup.move(self.posx, self.posy)
        self.visual_ui.popup.resize(self.popup_size)
        self.visual_ui.popup.setStyleSheet("""border-image: url(img/popup.png); color: white;
         padding-left: 10%;
         text-align: right;""")

    """
        Инициализация анимации
    """
    def init_animation(self):
        effect = QGraphicsOpacityEffect(self.visual_ui.popup)
        self.visual_ui.popup.setGraphicsEffect(effect)
        self.animation_opacity = QPropertyAnimation(effect, b"opacity")
        self.animation_opacity.setStartValue(0)
        self.animation_opacity.setEndValue(1)
        self.animation_opacity.setDuration(self.animation_duration + 2000)
        self.animation_opacity.setEasingCurve(QEasingCurve.OutExpo)
        self.animation_opacity1 = QPropertyAnimation(effect, b"opacity")
        self.animation_opacity1.setStartValue(1)
        self.animation_opacity1.setEndValue(self.opacity_end)
        self.animation_opacity1.setDuration(self.animation_duration)
        self.animation_opacity1.setEasingCurve(QEasingCurve.InCubic)

        self.anim_group = QSequentialAnimationGroup()
        self.anim_group.addAnimation(self.animation_opacity)
        self.anim_group.addAnimation(self.animation_opacity1)
        self.anim_group.start()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MyWidgetUi()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
