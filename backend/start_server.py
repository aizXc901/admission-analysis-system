import os
import sys
import django
from django.core.management import execute_from_command_line

def start_server():
    """Запуск сервера разработки Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
    django.setup()
    
    print("🚀 Запуск сервера разработки Django")
    print("🌐 Приложение будет доступно по адресу: http://127.0.0.1:8000")
    print("🔧 Для остановки сервера нажмите Ctrl+C")
    
    try:
        execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000'])
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")

if __name__ == "__main__":
    start_server()
