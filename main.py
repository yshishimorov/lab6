"""
Лабораторная работа №6: Веб-программирование на Python (Flask)
Вариант 1:
- Средняя сложность:
  1. Flask-приложение «Hello World»
  3. Статическая страница + CSS
  5. Страница с Bootstrap
- Повышенная сложность:
  1. Flask с базой SQLite (CRUD)
  4. Загрузка файла через форму

Студент: Шишиморов Ярослав Сергеевич
Группа: 221141
"""

import argparse
import sys
from app import create_app

def main():
    parser = argparse.ArgumentParser(description='Запуск веб-приложения Flask (Лабораторная работа №6)')
    parser.add_argument('--host', default='127.0.0.1', help='Хост для запуска (по умолчанию 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, help='Порт для запуска (по умолчанию 5000)')
    parser.add_argument('--no-debug', action='store_true', help='Отключить режим отладки')
    parser.add_argument('--check', action='store_true', help='Проверить корректность инициализации приложения и выйти')

    args = parser.parse_args()

    app = create_app()

    if args.check:
        print('=== ПРОВЕРКА КОНФИГУРАЦИИ ПРИЛОЖЕНИЯ ===')
        print(f'Имя приложения: {app.name}')
        print(f'База данных SQLite: {app.config["DATABASE_PATH"]}')
        print(f'Каталог загрузки файлов: {app.config["UPLOAD_FOLDER"]}')
        print('Зарегистрированные маршруты:')
        for rule in app.url_map.iter_rules():
            print(f'  [{rule.methods - {"HEAD", "OPTIONS"}}] {rule.rule} -> {rule.endpoint}')
        print('Конфигурация корректна, приложение готово к работе.')
        return

    print('=' * 65)
    print('  Лабораторная работа №6: Веб-приложение Flask (Вариант 1)')
    print('  Шишиморов Ярослав Сергеевич, группа 221141')
    print('=' * 65)
    print(f' Сервер запускается по адресу: http://{args.host}:{args.port}')
    print(' Для остановки нажмите Ctrl+C')
    print('=' * 65)

    app.run(
        host=args.host,
        port=args.port,
        debug=not args.no_debug
    )

if __name__ == '__main__':
    main()
