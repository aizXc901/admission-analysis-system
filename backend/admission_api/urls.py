from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
import os


def home_view(request):
    return HttpResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admission Analysis System</title>
        <meta charset="utf-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .container {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 800px;
                text-align: center;
            }}
            h1 {{ 
                color: #333;
                margin-bottom: 20px;
                font-size: 2.5em;
            }}
            .status {{
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 50px;
                display: inline-block;
                margin: 20px 0;
                font-weight: bold;
            }}
            .links {{
                margin: 30px 0;
            }}
            .links a {{
                display: block;
                background: #f5f5f5;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                color: #333;
                text-decoration: none;
                font-size: 1.1em;
                transition: all 0.3s;
            }}
            .links a:hover {{
                background: #667eea;
                color: white;
                transform: translateY(-2px);
            }}
            .info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎓 Система анализа поступления</h1>
            <p>Московская предпрофессиональная олимпиада</p>

            <div class="status">✅ СЕРВЕР РАБОТАЕТ</div>

            <div class="links">
                <a href="/admin/">🔐 Административная панель</a>
                <a href="/api/">📊 API система</a>
                <a href="/upload/">📁 Загрузка данных</a>
                <a href="/reports/">📈 Отчеты</a>
            </div>

            <div class="info">
                <h3>📋 Информация о системе:</h3>
                <p><strong>Логин:</strong> admin</p>
                <p><strong>Пароль:</strong> admin123</p>
                <p><strong>База данных:</strong> SQLite</p>
                <p><strong>Порт:</strong> 8000</p>
                <p><strong>Дата:</strong> 30.01.2026</p>
            </div>
        </div>
    </body>
    </html>
    """)


from university import views as university_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', university_views.api_home, name='api_home'),
    path('api/programs/', university_views.programs_list, name='programs_list'),
    path('upload/', university_views.upload_page, name='upload_page'),
    path('', home_view, name='home'),
]
