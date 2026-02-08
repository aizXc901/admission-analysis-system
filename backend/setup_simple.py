# backend/setup_simple.py
import os
import sys
import django

print("=== ПРОСТАЯ НАСТРОЙКА DJANGO ===")

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    print("✅ Django настроен")

    # Импортируем после setup
    from django.core.management import execute_from_command_line

    print("1. Создаем миграции...")
    execute_from_command_line(['manage.py', 'makemigrations', 'university'])

    print("2. Применяем миграции...")
    execute_from_command_line(['manage.py', 'migrate'])

    print("3. Создаем суперпользователя...")
    from django.contrib.auth import get_user_model

    User = get_user_model()

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@university.ru', 'admin123')
        print("   ✅ Создан: admin / admin123")
    else:
        print("   ℹ️ Уже существует")

    print("4. Создаем программы...")
    from university.models import EducationalProgram

    programs = [
        {'name': 'Прикладная математика', 'code': 'ПМ', 'capacity': 40},
        {'name': 'Информатика и вычислительная техника', 'code': 'ИВТ', 'capacity': 50},
        {'name': 'Инфокоммуникационные технологии и системы связи', 'code': 'ИТСС', 'capacity': 30},
        {'name': 'Информационная безопасность', 'code': 'ИБ', 'capacity': 20},
    ]

    for p in programs:
        obj, created = EducationalProgram.objects.get_or_create(
            code=p['code'],
            defaults=p
        )
        if created:
            print(f"   ✅ Создана: {p['name']}")

    print("\n🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("\nДля запуска сервера выполните:")
    print("python manage.py runserver 127.0.0.1:8000")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
