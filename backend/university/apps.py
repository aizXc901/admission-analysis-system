from django.apps import AppConfig


class UniversityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'university'
    verbose_name = 'Университетская система'

    def ready(self):
        # Можно добавить инициализацию здесь
        pass
