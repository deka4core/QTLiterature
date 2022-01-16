from PyQt5.QtWidgets import QWidget
from faq_ui import Ui_FAQ


class FAQWindow(QWidget, Ui_FAQ):
    """
        Инициализация окна справки
    """
    def __init__(self, visual_ui_class):
        super().__init__()
        self.visual_ui = visual_ui_class
        self.setupUi(self)
        self.faqTextEdit.setPlainText(open('README.md', 'r', encoding='utf8').read())
        self.visual_ui.faqButton.clicked.connect(self.open_window)

    """
        Открытие окна
    """
    def open_window(self):
        self.visual_ui.set_style_another(self)