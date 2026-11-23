import tempfile
import shutil
import unittest
from pathlib import Path
from app import create_app

class CrudTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / 'test_crud.db')
        self.app = create_app({
            'TESTING': True,
            'DATABASE_PATH': self.db_path,
            'UPLOAD_FOLDER': str(Path(self.temp_dir) / 'uploads'),
            'SECRET_KEY': 'test-secret',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_notes_list(self):
        """Тест чтения списка заметок (Read All)."""
        response = self.client.get('/notes')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Управление заметками', content)
        self.assertIn('Добро пожаловать в лабораторную работу №6', content)

    def test_notes_search(self):
        """Тест поиска заметок по тексту."""
        response = self.client.get('/notes?search=SQLite')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Памятка по SQLite', content)

    def test_notes_category_filter(self):
        """Тест фильтрации заметок по категории."""
        response = self.client.get('/notes?category=Разработка')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Архитектура Flask-приложения', content)

    def test_note_detail_success(self):
        """Тест детального просмотра заметки (Read One)."""
        response = self.client.get('/notes/1')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Добро пожаловать в лабораторную работу №6', content)

    def test_note_detail_not_found(self):
        """Тест 404 для несуществующей заметки."""
        response = self.client.get('/notes/99999')
        self.assertEqual(response.status_code, 404)

    def test_note_create_page_get(self):
        """Тест формы создания заметки."""
        response = self.client.get('/notes/create')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Создание новой заметки', response.data.decode('utf-8'))

    def test_note_create_success(self):
        """Тест успешного создания новой заметки (Create)."""
        payload = {
            'title': 'Тестовая заметка студента',
            'category': 'Тестирование',
            'content': 'Подробное описание создаваемой тестовой заметки.'
        }
        response = self.client.post('/notes/create', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Тестовая заметка студента', content)
        self.assertIn('успешно создана', content)

    def test_note_create_validation_empty_title(self):
        """Тест валидации создания заметки: пустой заголовок."""
        payload = {'title': '', 'category': 'Тест', 'content': 'Текст'}
        response = self.client.post('/notes/create', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Пожалуйста, укажите заголовок заметки', content)

    def test_note_create_validation_empty_content(self):
        """Тест валидации создания заметки: пустой текст."""
        payload = {'title': 'Заголовок', 'category': 'Тест', 'content': ''}
        response = self.client.post('/notes/create', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Пожалуйста, введите текст заметки', content)

    def test_note_edit_get(self):
        """Тест отображения формы редактирования (Update GET)."""
        response = self.client.get('/notes/1/edit')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Редактирование заметки', response.data.decode('utf-8'))

    def test_note_edit_post_success(self):
        """Тест сохранения изменений заметки (Update POST)."""
        payload = {
            'title': 'Обновленный заголовок',
            'category': 'Новая категория',
            'content': 'Обновленное содержание заметки.'
        }
        response = self.client.post('/notes/1/edit', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Обновленный заголовок', content)
        self.assertIn('успешно обновлена', content)

    def test_note_delete(self):
        """Тест удаления заметки (Delete)."""
        # Удаляем существующую начальную заметку (ID = 1)
        response = self.client.post('/notes/1/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('успешно удалена', content)
        
        # Проверяем, что запрос к ней теперь возвращает 404
        resp_detail = self.client.get('/notes/1')
        self.assertEqual(resp_detail.status_code, 404)

if __name__ == '__main__':
    unittest.main()
