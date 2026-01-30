# backend/test_django.py
import os
import sys
import django

print("=== ТЕСТ DJANGO ===")

# Добавляем текущую директорию
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
    django.setup()
    print("✅ Django настроен успешно")

    # Проверяем модели
    from university.models import EducationalProgram

    print("✅ Модели загружены")

    # Проверяем настройки
    from django.conf import settings

    print(f"✅ DEBUG = {settings.DEBUG}")
    print(f"✅ DATABASE = {settings.DATABASES['default']['ENGINE']}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
