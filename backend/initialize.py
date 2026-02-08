#!/usr/bin/env python
"""
Инициализация системы Admission Analysis System
Запустите этот файл для настройки всего проекта
"""
import os
import sys
import django
import subprocess
import time


def setup_django():
    """Настройка Django окружения"""
    print("🔧 Настройка Django...")

    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Устанавливаем настройки Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')

    try:
        django.setup()
        print("✅ Django настроен успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка настройки Django: {e}")
        return False


def create_migrations():
    """Создание миграций"""
    print("\n📦 Создание миграций...")
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "makemigrations", "university"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr and "No changes detected" not in result.stderr:
            print(f"⚠️  Предупреждение: {result.stderr}")

        print("✅ Миграции созданы")
        return True
    except Exception as e:
        print(f"❌ Ошибка создания миграций: {e}")
        return False


def apply_migrations():
    """Применение миграций"""
    print("\n🚀 Применение миграций...")
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  Предупреждение: {result.stderr}")

        print("✅ Миграции применены")
        return True
    except Exception as e:
        print(f"❌ Ошибка применения миграций: {e}")
        return False


def create_superuser():
    """Создание суперпользователя"""
    print("\n👑 Создание администратора...")

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.filter(username='admin').exists():
            print("ℹ️  Администратор уже существует")
            return True

        User.objects.create_superuser(
            username='admin',
            email='admin@university.ru',
            password='admin123'
        )
        print("✅ Администратор создан")
        print("   Логин: admin")
        print("   Пароль: admin123")
        print("   Email: admin@university.ru")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания администратора: {e}")
        return False


def create_educational_programs():
    """Создание образовательных программ"""
    print("\n🎓 Создание образовательных программ...")

    try:
        from university.models import EducationalProgram

        programs = [
            {
                'name': 'Прикладная математика',
                'code': 'ПМ',
                'slug': 'pm',
                'capacity': 40,
                'description': 'Программа подготовки специалистов в области прикладной математики'
            },
            {
                'name': 'Информатика и вычислительная техника',
                'code': 'ИВТ',
                'slug': 'ivt',
                'capacity': 50,
                'description': 'Программа подготовки специалистов в области информатики и вычислительной техники'
            },
            {
                'name': 'Инфокоммуникационные технологии и системы связи',
                'code': 'ИТСС',
                'slug': 'itss',
                'capacity': 30,
                'description': 'Программа подготовки специалистов в области инфокоммуникационных технологий'
            },
            {
                'name': 'Информационная безопасность',
                'code': 'ИБ',
                'slug': 'ib',
                'capacity': 20,
                'description': 'Программа подготовки специалистов в области информационной безопасности'
            },
        ]

        created_count = 0
        for program_data in programs:
            program, created = EducationalProgram.objects.get_or_create(
                code=program_data['code'],
                defaults=program_data
            )
            if created:
                created_count += 1
                print(f"   ✅ Создана: {program.name}")
            else:
                print(f"   ℹ️  Уже существует: {program.name}")

        print(f"✅ Создано {created_count} программ")
        return True

    except Exception as e:
        print(f"❌ Ошибка создания программ: {e}")
        return False


def check_database():
    """Проверка базы данных"""
    print("\n🔍 Проверка базы данных...")

    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✅ База данных существует: {size} байт")
            return True
        else:
            print("❌ База данных не найдена")
            return False
    except Exception as e:
        print(f"❌ Ошибка проверки базы: {e}")
        return False


def start_server():
    """Запуск сервера"""
    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК СЕРВЕРА")
    print("=" * 60)

    print("\nДля запуска сервера выполните в новом терминале:")
    print("cd C:\\Users\\maria\\PycharmProjects\\admission-analysis-system\\backend")
    print("python manage.py runserver 127.0.0.1:8000")

    print("\nИли запустите файл: start_server.bat")

    print("\n🌐 Откройте в браузере:")
    print("👉 http://127.0.0.1:8000/")
    print("👉 http://127.0.0.1:8000/admin/")

    print("\n🔑 Данные для входа:")
    print("Логин: admin")
    print("Пароль: admin123")


def main():
    """Основная функция"""
    print("=" * 60)
    print("🎓 ADMISSION ANALYSIS SYSTEM - ИНИЦИАЛИЗАЦИЯ")
    print("=" * 60)

    # Шаг 1: Настройка Django
    if not setup_django():
        return

    # Шаг 2: Создание миграций
    if not create_migrations():
        print("⚠️  Продолжаем без создания миграций...")

    # Шаг 3: Применение миграций
    if not apply_migrations():
        print("⚠️  Продолжаем без применения миграций...")

    # Шаг 4: Создание администратора
    if not create_superuser():
        print("⚠️  Продолжаем без создания администратора...")

    # Шаг 5: Создание образовательных программ
    if not create_educational_programs():
        print("⚠️  Продолжаем без создания программ...")

    # Шаг 6: Проверка базы данных
    check_database()

    # Шаг 7: Инструкция по запуску
    start_server()

    print("\n" + "=" * 60)
    print("✅ ИНИЦИАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


if __name__ == "__main__":
    main()
