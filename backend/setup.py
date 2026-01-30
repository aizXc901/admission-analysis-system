import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line


def setup_project():
    print("🚀 Установка и инициализация проекта 'Система анализа поступления'")
    print("=" * 60)

    # Устанавливаем зависимости
    print("\n📦 Установка зависимостей...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Активируем настройки Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
    django.setup()

    print("\n🔄 Выполнение миграций базы данных...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])

    print("\n🔑 Создание суперпользователя (необязательно)...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser', '--noinput'])
    except:
        print("⚠️  Пропуск создания суперпользователя (уже существует или ошибка)")

    print("\n✅ Проект успешно инициализирован!")
    print("🌐 Для запуска сервера выполните: python manage.py runserver")


if __name__ == "__main__":
    setup_project()
