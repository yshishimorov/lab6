import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Базовая конфигурация Flask-приложения."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-study-lab6')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', str(BASE_DIR / 'instance' / 'app.db'))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'json', 'md'}

class TestConfig(Config):
    """Конфигурация для запуска тестов."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    DATABASE_PATH = ':memory:'
    WTF_CSRF_ENABLED = False
