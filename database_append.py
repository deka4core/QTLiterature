from PyQt5.QtWidgets import QWidget, QFileDialog
from database_append_ui import Ui_AppBook
import sqlite3


class AppendError(Exception):
    pass


class BookTitleIsNull(AppendError):
    pass


class AuthorTitleIsNull(AppendError):
    pass


class AppendBook(QWidget, Ui_AppBook):
    def __init__(self, visual_ui_class):
        super().__init__()
        self.visual_ui = visual_ui_class
        self.setupUi(self)
        self.visual_ui.addBookButton.clicked.connect(self.open_window)
        file_name = 'literature_db.db'
        self.connection_db = sqlite3.connect(file_name)
        self.cursor = self.connection_db.cursor()
        genres = self.cursor.execute('''select title from genres''').fetchall()
        for i in genres:
            self.cBoxFileGenre.addItem(i[0])
        self.openFileButton.clicked.connect(self.open_file)
        self.appendButton.clicked.connect(self.append_file)

    def open_window(self):
        self.visual_ui.set_style_another(self)

    def open_file(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выбрать книгу (txt)', '',
                                                 'Текстовый файл (*.txt)')[0]
        self.errorLabel.setText(self.fname)

    def append_file(self):
        try:
            book_title = self.editFileName.text() if self.editFileName.text() != '' else None
            book_genre = self.cBoxFileGenre.currentText()
            author_title = self.editAuthorName.text() if self.editAuthorName.text() != '' else None
            if book_title is not None:
                if author_title is not None:
                    author_id = self.cursor.execute(f"""select id from authors where
                     title = '{author_title}'""").fetchone()
                    print(author_id)
                    if author_id is None:
                        self.cursor.execute(f"""insert into authors(title) values('{author_title}')""")
                        author_id = \
                            self.cursor.execute(f"""select id from authors where
                             title = '{author_title}'""").fetchone()[0]
                        self.cursor.execute(f"""insert into books(title, genreId, authorId, path) 
                            values('{book_title}', (select id from genres where title = '{book_genre}'),
                            {str(author_id)}, '{self.fname}')""")
                    else:
                        self.cursor.execute(f"""insert into books(title, genreId, authorId, path) 
                                                    values('{book_title}', (select id from genres
                                                     where title = '{book_genre}'),
                                                    {str(author_id[0])}, '{self.fname}')""")
                    self.connection_db.commit()
                else:
                    raise AuthorTitleIsNull
            else:
                raise BookTitleIsNull
            self.close()
        except BookTitleIsNull:
            self.errorLabel.setText('Введите название книги...')
        except AuthorTitleIsNull:
            self.errorLabel.setText('Введите фамилию автора...')
