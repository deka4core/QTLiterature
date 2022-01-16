import os
import pickle

SQL_EXECUTION = '''select books.title, genres.title, authors.title
         from books left join genres on books.genreId = genres.id 
         join authors on books.authorId = authors.id'''
SEARCH_HAS_EXTRA_PARAMETERS = False
EXTRA_PARAM = ['', '']
FILE_DB_NAME = 'literature_db.db'
CSS_FILE_NAME = 'stylesheet_white.css'
MAIN_IS_OPENED = False
BOOK_OPENED_PATH = ''
CURRENT_BOOK = []
CURRENT_PAGE = 0
target = "bookmarks.bin"
if os.path.getsize(target) > 0:
    with open(target, "rb") as f:
        unpickler = pickle.Unpickler(f)
        BOOKMARKS = unpickler.load()
else:
    BOOKMARKS = {}
