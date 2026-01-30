# backend/debug_server.py
import os
import sys
import django
from django.core.management import execute_from_command_line

print("=" * 60)
print("🐛 DEBUG SERVER")
print("=" * 60)

# Принудительно устанавливаем настройки
os.environ['DJANGO_SETTINGS_MODULE'] = 'admission_api.settings'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    print("✅ Django setup successful")

    # Показываем настройки
    from django.conf import settings

    print(f"DEBUG: {settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"DATABASE: {settings.DATABASES['default']['ENGINE']}")

    # Запускаем сервер
    print("\n🚀 Starting server...")
    execute_from_command_line(['', 'runserver', '127.0.0.1:8000', '--noreload'])

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
    input("\nPress Enter to exit...")
