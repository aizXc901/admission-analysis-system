import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admission_api.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Создаем суперпользователя если его нет
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@university.ru',
        password='admin123'
    )
    print('✅ Суперпользователь создан!')
    print('   Логин: admin')
    print('   Пароль: admin123')
    print('   Email: admin@university.ru')
else:
    print('ℹ️ Суперпользователь admin уже существует')

# Создаем еще одного тестового пользователя
if not User.objects.filter(username='test').exists():
    User.objects.create_superuser(
        username='test',
        email='test@university.ru',
        password='test123'
    )
    print('✅ Тестовый пользователь создан!')
    print('   Логин: test')
    print('   Пароль: test123')