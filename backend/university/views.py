from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import EducationalProgram, Applicant, Application
import json

def api_home(request):
    """Главная страница API"""
    return JsonResponse({
        'system': 'Admission Analysis System',
        'version': '1.0.0',
        'endpoints': {
            'programs': '/api/programs/',
            'applicants': '/api/applicants/',
            'applications': '/api/applications/',
            'upload': '/api/upload/',
            'calculate': '/api/calculate/',
        }
    })

def programs_list(request):
    """Список образовательных программ"""
    programs = EducationalProgram.objects.all()
    data = [{
        'id': p.id,
        'name': p.name,
        'code': p.code,
        'capacity': p.capacity,
        'slug': p.slug,
    } for p in programs]
    return JsonResponse({'programs': data})

def upload_page(request):
    """Страница загрузки файлов"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Загрузка данных</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; }
            form { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            input, select { margin: 10px 0; padding: 10px; width: 100%; }
            button { background: #4CAF50; color: white; padding: 15px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📁 Загрузка CSV файлов</h1>
            <form id="uploadForm">
                <select name="program">
                    <option value="ПМ">Прикладная математика (ПМ)</option>
                    <option value="ИВТ">Информатика и вычислительная техника (ИВТ)</option>
                    <option value="ИТСС">Инфокоммуникационные технологии (ИТСС)</option>
                    <option value="ИБ">Информационная безопасность (ИБ)</option>
                </select>
                <input type="date" name="date" value="2026-08-01">
                <input type="file" name="file" accept=".csv">
                <button type="submit">Загрузить</button>
            </form>
            <div id="result"></div>
        </div>
        <script>
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                const formData = new FormData(e.target);
                const response = await fetch('/api/upload/', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    `<pre>${JSON.stringify(result, null, 2)}</pre>`;
            };
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)
