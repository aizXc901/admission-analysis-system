# backend/setup.py
import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')

try:
    import django

    django.setup()

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Создаем суперпользователя
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@university.ru',
            password='admin123'
        )
        print("✅ Суперпользователь 'admin' создан!")
    else:
        print("ℹ️ Суперпользователь 'admin' уже существует")

    # Создаем образовательные программы
    from university.models import EducationalProgram

    programs = [
        {'name': 'Прикладная математика', 'code': 'ПМ', 'slug': 'pm', 'capacity': 40},
        {'name': 'Информатика и вычислительная техника', 'code': 'ИВТ', 'slug': 'ivt', 'capacity': 50},
        {'name': 'Инфокоммуникационные технологии и системы связи', 'code': 'ИТСС', 'slug': 'itss', 'capacity': 30},
        {'name': 'Информационная безопасность', 'code': 'ИБ', 'slug': 'ib', 'capacity': 20},
    ]

    for prog in programs:
        program, created = EducationalProgram.objects.get_or_create(
            code=prog['code'],
            defaults=prog
        )
        if created:
            print(f"✅ Создана программа: {prog['name']}")
        else:
            print(f"ℹ️ Программа уже существует: {prog['name']}")

    print("\n🎉 Настройка завершена!")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()
