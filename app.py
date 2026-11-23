import os
from pathlib import Path
from flask import Flask

from src.config import Config
from src.database import close_db, init_db
from src.routes import main_bp

def create_app(test_config=None):
    """Фабрика приложений Flask."""
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # Загружаем базовую конфигурацию
    app.config.from_object(Config)

    # Если переданы параметры для тестирования - перезаписываем
    if test_config is not None:
        app.config.from_mapping(test_config)

    # Гарантируем наличие необходимых каталогов
    db_path = app.config.get('DATABASE_PATH')
    if db_path and not str(db_path).startswith(':memory:') and not str(db_path).startswith('file:'):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        Path(upload_folder).mkdir(parents=True, exist_ok=True)

    # Регистрация функций жизненного цикла БД
    app.teardown_appcontext(close_db)

    # Регистрация маршрутов
    app.register_blueprint(main_bp)

    # Инициализация таблиц БД
    init_db(app)

    return app

# Экземпляр приложения по умолчанию
app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
