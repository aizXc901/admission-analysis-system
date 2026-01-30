# backend/init_project.py
import os
import sys
import subprocess
import time


def run_command(cmd, description):
    print(f"\n{'=' * 60}")
    print(f"{description}")
    print(f"{'=' * 60}")
    print(f"Команда: {cmd}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.stdout:
            print("Вывод:")
            print(result.stdout)

        if result.stderr:
            print("Ошибки:")
            print(result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} - УСПЕШНО")
            return True
        else:
            print(f"❌ {description} - ОШИБКА")
            return False

    except Exception as e:
        print(f"❌ Исключение: {e}")
        return False


def main():
    print("🚀 ПОЛНАЯ ИНИЦИАЛИЗАЦИЯ ПРОЕКТА ADMISSION ANALYSIS SYSTEM")
    print("=" * 60)

    # 1. Проверяем Python
    if not run_command("python --version", "Проверка Python"):
        return

    # 2. Удаляем старую базу
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("🗑️  Удалена старая база данных")

    # 3. Создаем миграции
    if not run_command("python manage.py makemigrations university --verbosity 3", "Создание миграций"):
        return

    # 4. Применяем миграции
    if not run_command("python manage.py migrate --verbosity 3", "Применение миграций"):
        return

    # 5. Создаем суперпользователя
    create_admin_cmd = """
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@university.ru', 'admin123')
    print('✅ Создан суперпользователь: admin / admin123')
else:
    print('ℹ️ Суперпользователь уже существует')
"""

    with open("temp_create_admin.py", "w", encoding="utf-8") as f:
        f.write(create_admin_cmd)

    run_command("python manage.py shell < temp_create_admin.py", "Создание администратора")
    os.remove("temp_create_admin.py")

    # 6. Создаем образовательные программы
    create_programs_cmd = """
from university.models import EducationalProgram
programs = [
    {'name': 'Прикладная математика', 'code': 'ПМ', 'slug': 'pm', 'capacity': 40},
    {'name': 'Информатика и вычислительная техника', 'code': 'ИВТ', 'slug': 'ivt', 'capacity': 50},
    {'name': 'Инфокоммуникационные технологии и системы связи', 'code': 'ИТСС', 'slug': 'itss', 'capacity': 30},
    {'name': 'Информационная безопасность', 'code': 'ИБ', 'slug': 'ib', 'capacity': 20},
]
for p in programs:
    obj, created = EducationalProgram.objects.get_or_create(code=p['code'], defaults=p)
    if created: print(f'✅ Создана: {p[\"name\"]}')
    else: print(f'ℹ️ Существует: {p[\"name\"]}')
"""

    with open("temp_create_programs.py", "w", encoding="utf-8") as f:
        f.write(create_programs_cmd)

    run_command("python manage.py shell < temp_create_programs.py", "Создание образовательных программ")
    os.remove("temp_create_programs.py")

    print("\n" + "=" * 60)
    print("🎉 ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 60)
    print("\nДля запуска сервера выполните:")
    print("  python manage.py runserver")
    print("\nАдрес сервера: http://127.0.0.1:8000/")
    print("Админка: http://127.0.0.1:8000/admin/")
    print("Логин: admin")
    print("Пароль: admin123")


if __name__ == "__main__":
    main()
