import os
from datetime import datetime
from pathlib import Path
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, send_from_directory, current_app, abort
)
from werkzeug.utils import secure_filename

from src.database import (
    get_all_notes, get_note_by_id, create_note,
    update_note, delete_note, get_categories
)

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    """Проверка допустимости расширения файла."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def get_uploaded_files_info():
    """Получить список и метаданные всех загруженных файлов."""
    upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
    if not upload_folder.exists():
        upload_folder.mkdir(parents=True, exist_ok=True)
    
    files = []
    for file_path in upload_folder.iterdir():
        if file_path.is_file() and file_path.name != '.gitkeep':
            stat = file_path.stat()
            size_kb = round(stat.st_size / 1024, 2)
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M:%S')
            files.append({
                'name': file_path.name,
                'size_kb': size_kb,
                'modified': modified,
                'ext': file_path.suffix.lower().lstrip('.')
            })
    files.sort(key=lambda x: x['name'].lower())
    return files

# -------------------------------------------------------------
# Главная страница и Hello World
# -------------------------------------------------------------
@main_bp.route('/')
def index():
    """Главная страница со сводкой по варианту 1 и навигацией."""
    notes_count = len(get_all_notes())
    files_count = len(get_uploaded_files_info())
    return render_template('index.html', notes_count=notes_count, files_count=files_count)

@main_bp.route('/hello')
def hello_world():
    """Задание средней сложности №1: Flask-приложение «Hello World»."""
    # Возвращаем шаблон с красивым оформлением и сырой строкой для проверки
    name = request.args.get('name', 'Мир')
    return render_template('hello.html', name=name)

# -------------------------------------------------------------
# Задание средней сложности №3: Статическая страница + CSS
# -------------------------------------------------------------
@main_bp.route('/static-demo')
def static_demo():
    """Задание средней сложности №3: Демонстрация статической страницы с авторским CSS."""
    return render_template('static_demo.html')

# -------------------------------------------------------------
# Задание повышенной сложности №1: Flask с базой SQLite (CRUD)
# -------------------------------------------------------------
@main_bp.route('/notes')
def notes_list():
    """Просмотр всех заметок с поиском и фильтром по категориям (Read All)."""
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'Все').strip()
    
    notes = get_all_notes(search_query=search if search else None, category=category if category != 'Все' else None)
    categories = get_categories()
    
    return render_template(
        'items/list.html',
        notes=notes,
        categories=categories,
        current_category=category,
        current_search=search
    )

@main_bp.route('/notes/<int:note_id>')
def note_detail(note_id):
    """Просмотр одной заметки (Read One)."""
    note = get_note_by_id(note_id)
    if note is None:
        abort(404, description='Заметка не найдена.')
    return render_template('items/detail.html', note=note)

@main_bp.route('/notes/create', methods=['GET', 'POST'])
def note_create():
    """Создание новой заметки (Create)."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Общее').strip()
        content = request.form.get('content', '').strip()

        if not title:
            flash('Пожалуйста, укажите заголовок заметки.', 'danger')
            return render_template('items/create.html', title=title, category=category, content=content)
        
        if not content:
            flash('Пожалуйста, введите текст заметки.', 'danger')
            return render_template('items/create.html', title=title, category=category, content=content)

        new_id = create_note(title, category, content)
        flash(f'Заметка «{title}» успешно создана (ID: {new_id})!', 'success')
        return redirect(url_for('main.notes_list'))

    return render_template('items/create.html', category='Общее')

@main_bp.route('/notes/<int:note_id>/edit', methods=['GET', 'POST'])
def note_edit(note_id):
    """Редактирование заметки (Update)."""
    note = get_note_by_id(note_id)
    if note is None:
        abort(404, description='Заметка для редактирования не найдена.')

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', 'Общее').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('Заголовок и содержание не могут быть пустыми.', 'danger')
            return render_template('items/edit.html', note=note)

        update_note(note_id, title, category, content)
        flash(f'Заметка #{note_id} успешно обновлена!', 'success')
        return redirect(url_for('main.note_detail', note_id=note_id))

    return render_template('items/edit.html', note=note)

@main_bp.route('/notes/<int:note_id>/delete', methods=['POST'])
def note_delete(note_id):
    """Удаление заметки (Delete)."""
    note = get_note_by_id(note_id)
    if note is None:
        abort(404, description='Заметка для удаления не найдена.')

    delete_note(note_id)
    flash(f'Заметка «{note["title"]}» успешно удалена.', 'info')
    return redirect(url_for('main.notes_list'))

# -------------------------------------------------------------
# Задание повышенной сложности №4: Загрузка файла через форму
# -------------------------------------------------------------
@main_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """Форма загрузки файла и просмотр списка загруженных файлов."""
    upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
    upload_folder.mkdir(parents=True, exist_ok=True)

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не был выбран в запросе.', 'warning')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран. Выберите файл для загрузки.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not filename:
                filename = 'uploaded_file'
            
            save_path = upload_folder / filename
            file.save(str(save_path))
            flash(f'Файл «{filename}» успешно загружен на сервер!', 'success')
            return redirect(url_for('main.upload_file'))
        else:
            allowed = ', '.join(sorted(current_app.config['ALLOWED_EXTENSIONS']))
            flash(f'Недопустимый тип файла. Разрешены форматы: {allowed}', 'danger')
            return redirect(request.url)

    files = get_uploaded_files_info()
    allowed_exts = sorted(current_app.config['ALLOWED_EXTENSIONS'])
    return render_template('uploads/upload.html', files=files, allowed_exts=allowed_exts)

@main_bp.route('/downloads/<path:filename>')
def download_file(filename):
    """Скачивание загруженного файла с сервера."""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename, as_attachment=True)

@main_bp.route('/uploads/<path:filename>/delete', methods=['POST'])
def delete_uploaded_file(filename):
    """Удаление загруженного файла."""
    safe_name = secure_filename(filename)
    file_path = Path(current_app.config['UPLOAD_FOLDER']) / safe_name
    if file_path.exists() and file_path.is_file() and safe_name != '.gitkeep':
        file_path.unlink()
        flash(f'Файл «{safe_name}» успешно удалён.', 'info')
    else:
        flash('Файл не найден или защищён от удаления.', 'warning')
    return redirect(url_for('main.upload_file'))
