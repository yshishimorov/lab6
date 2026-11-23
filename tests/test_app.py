import tempfile
import shutil
import unittest
from pathlib import Path
from app import create_app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = str(Path(self.temp_dir) / 'test_app.db')
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

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Лабораторная работа №6', content)
        self.assertIn('Шишиморов Ярослав Сергеевич', content)
        self.assertIn('221141', content)
        self.assertIn('Вариант 1', content)

    def test_hello_world_default(self):
        """Тест задания средней сложности №1: Flask Hello World (по умолчанию)."""
        response = self.client.get('/hello')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Hello, Мир!', content)

    def test_hello_world_custom_query_param(self):
        """Тест задания средней сложности №1: Flask Hello World с параметром."""
        response = self.client.get('/hello?name=Ярослав')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Hello, Ярослав!', content)

    def test_static_css_served(self):
        """Тест задания средней сложности №3: Обслуживание статического CSS-файла."""
        response = self.client.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/css', response.headers.get('Content-Type', ''))
        content = response.data.decode('utf-8')
        self.assertIn('--brand-primary', content)

    def test_static_demo_page(self):
        """Тест задания средней сложности №3: Страница со стилями CSS."""
        response = self.client.get('/static-demo')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Статическая страница и пользовательские стили CSS', content)

    def test_bootstrap_included(self):
        """Тест задания средней сложности №5: Наличие компонентов Bootstrap 5."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('bootstrap.min.css', content)
        self.assertIn('navbar', content)
        self.assertIn('container', content)

    def test_404_not_found(self):
        response = self.client.get('/non-existent-route-xyz')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
