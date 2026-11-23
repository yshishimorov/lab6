import sqlite3
from datetime import datetime
from pathlib import Path
from flask import current_app, g

def get_db():
    """Получение подключения к SQLite для текущего контекста запроса."""
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE_PATH', 'instance/app.db')
        is_uri = str(db_path).startswith('file:')
        if not is_uri and str(db_path) != ':memory:':
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(
            db_path,
            uri=is_uri
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Закрытие соединения с БД при завершении запроса."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app=None):
    """Инициализация таблиц базы данных и начальных данных."""
    def _execute(db):
        db.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'Общее',
                content TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now', 'localtime')),
                updated_at TEXT DEFAULT (datetime('now', 'localtime'))
            );
        ''')
        db.commit()

        # Заполняем начальными данными, если таблица пуста
        count = db.execute('SELECT COUNT(*) FROM notes').fetchone()[0]
        if count == 0:
            demo_notes = [
                (
                    'Добро пожаловать в лабораторную работу №6',
                    'Учёба',
                    'Приложение демонстрирует работу маршрутизации Flask, стилизации CSS/Bootstrap, '
                    'а также CRUD-операции с SQLite и загрузку файлов.'
                ),
                (
                    'Архитектура Flask-приложения',
                    'Разработка',
                    'Использован паттерн Application Factory (create_app), Blueprints для модульности '
                    'и шаблонизатор Jinja2 с наследованием базового шаблона.'
                ),
                (
                    'Памятка по SQLite',
                    'Базы данных',
                    'Операции CRUD: Create (INSERT), Read (SELECT), Update (UPDATE), Delete (DELETE). '
                    'Все запросы используют параметризацию для защиты от SQL-инъекций.'
                )
            ]
            db.executemany(
                '''INSERT INTO notes (title, category, content, created_at, updated_at) 
                   VALUES (?, ?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))''',
                demo_notes
            )
            db.commit()

    if app is not None:
        with app.app_context():
            db = get_db()
            _execute(db)
    else:
        db = get_db()
        _execute(db)

def get_all_notes(search_query=None, category=None):
    """Получить все заметки с возможностью поиска и фильтрации."""
    db = get_db()
    sql = 'SELECT * FROM notes WHERE 1=1'
    params = []

    if category and category != 'Все':
        sql += ' AND category = ?'
        params.append(category)

    if search_query:
        sql += ' AND (title LIKE ? OR content LIKE ?)'
        wildcard = f'%{search_query.strip()}%'
        params.extend([wildcard, wildcard])

    sql += ' ORDER BY id DESC'
    return db.execute(sql, params).fetchall()

def get_note_by_id(note_id):
    """Получить заметку по её идентификатору."""
    db = get_db()
    return db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()

def create_note(title, category, content):
    """Создать новую заметку."""
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO notes (title, category, content, created_at, updated_at) 
           VALUES (?, ?, ?, datetime('now', 'localtime'), datetime('now', 'localtime'))''',
        (title.strip(), category.strip(), content.strip())
    )
    db.commit()
    return cursor.lastrowid

def update_note(note_id, title, category, content):
    """Обновить существующую заметку."""
    db = get_db()
    db.execute(
        '''UPDATE notes 
           SET title = ?, category = ?, content = ?, updated_at = datetime('now', 'localtime') 
           WHERE id = ?''',
        (title.strip(), category.strip(), content.strip(), note_id)
    )
    db.commit()

def delete_note(note_id):
    """Удалить заметку по ID."""
    db = get_db()
    db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    db.commit()

def get_categories():
    """Получить список всех уникальных категорий заметок."""
    db = get_db()
    rows = db.execute('SELECT DISTINCT category FROM notes ORDER BY category').fetchall()
    return [row['category'] for row in rows]
