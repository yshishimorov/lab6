import io
import shutil
import tempfile
import unittest
from pathlib import Path

from app import create_app

class UploadTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_upload_dir = str(Path(self.temp_dir) / 'uploads')
        self.db_path = str(Path(self.temp_dir) / 'test_upload.db')
        self.app = create_app({
            'TESTING': True,
            'DATABASE_PATH': self.db_path,
            'UPLOAD_FOLDER': self.temp_upload_dir,
            'SECRET_KEY': 'test-secret',
            'WTF_CSRF_ENABLED': False
        })
        self.client = self.app.test_client()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upload_page_get(self):
        """Тест загрузки страницы формы файлов."""
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Загрузка файла через веб-форму', content)
        self.assertIn('txt', content)

    def test_upload_valid_file(self):
        """Тест успешной загрузки текстового файла."""
        data = {
            'file': (io.BytesIO(b'Hello Flask file upload content'), 'sample_test.txt')
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('успешно загружен', content)
        self.assertIn('sample_test.txt', content)

        # Проверяем фактическое наличие на диске
        saved_file = Path(self.temp_upload_dir) / 'sample_test.txt'
        self.assertTrue(saved_file.exists())
        self.assertEqual(saved_file.read_bytes(), b'Hello Flask file upload content')

    def test_upload_invalid_extension(self):
        """Тест отклонения файла с недопустимым расширением (.exe)."""
        data = {
            'file': (io.BytesIO(b'binary data'), 'malicious.exe')
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Недопустимый тип файла', content)

        saved_file = Path(self.temp_upload_dir) / 'malicious.exe'
        self.assertFalse(saved_file.exists())

    def test_upload_no_file(self):
        """Тест отправки формы без выбора файла."""
        response = self.client.post('/upload', data={}, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Файл не был выбран в запросе', content)

    def test_download_uploaded_file(self):
        """Тест скачивания загруженного файла."""
        test_file = Path(self.temp_upload_dir) / 'download_me.txt'
        test_file.write_text('Downloaded content', encoding='utf-8')

        response = self.client.get('/downloads/download_me.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Downloaded content')

    def test_delete_uploaded_file(self):
        """Тест удаления загруженного файла."""
        test_file = Path(self.temp_upload_dir) / 'delete_me.txt'
        test_file.write_text('Delete this', encoding='utf-8')
        self.assertTrue(test_file.exists())

        response = self.client.post('/uploads/delete_me.txt/delete', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('успешно удалён', content)
        self.assertFalse(test_file.exists())

if __name__ == '__main__':
    unittest.main()
