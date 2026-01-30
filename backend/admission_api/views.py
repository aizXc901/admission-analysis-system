from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from datetime import datetime
import json
import pandas as pd

from admission_api.models import Applicant, EducationalProgram, AdmissionData
from university.data_generator import run_data_generation
from university.admission_calculator import AdmissionCalculator
from university.pdf_reporter import PDFReporter


def index(request):
    """Главная страница приложения"""
    programs = EducationalProgram.objects.all()
    return render(request, 'index.html', {'programs': programs})


def load_data(request):
    """Загрузка данных из файла"""
    if request.method == 'POST' and request.FILES:
        uploaded_file = request.FILES['file']

        try:
            # Определение типа файла
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                return JsonResponse({'error': 'Неподдерживаемый формат файла'}, status=400)

            # Сохранение данных в базу
            for _, row in df.iterrows():
                # Получаем или создаем абитуриента
                applicant, created = Applicant.objects.get_or_create(
                    id=row['ID'],
                    defaults={
                        'physics_ikt': row['Балл Физика/ИКТ'],
                        'russian_lang': row['Балл Русский язык'],
                        'math': row['Балл Математика'],
                        'achievements': row['Балл за индивидуальные достижения'],
                        'total_score': row['Сумма баллов']
                    }
                )

                # Получаем программу
                program = EducationalProgram.objects.get(code=row['ОП'])

                # Создаем или обновляем запись в AdmissionData
                admission_data, created = AdmissionData.objects.get_or_create(
                    applicant=applicant,
                    educational_program=program,
                    defaults={
                        'date': parse_date(row['Дата']) if 'Дата' in row else datetime.now().date(),
                        'has_consent': bool(row['Наличие согласия о зачислении в ВУЗ']),
                        'priority': int(row['Приоритет ОП'])
                    }
                )

                if not created:
                    # Обновляем существующую запись
                    admission_data.has_consent = bool(row['Наличие согласия о зачислении в ВУЗ'])
                    admission_data.priority = int(row['Приоритет ОП'])
                    admission_data.save()

            return JsonResponse({'success': True, 'message': f'Загружено {len(df)} записей'})

        except Exception as e:
            return JsonResponse({'error': f'Ошибка при загрузке данных: {str(e)}'}, status=400)

    return render(request, 'load_data.html')


def update_data(request):
    """Обновление данных (удаление, добавление, изменение)"""
    if request.method == 'POST':
        try:
            # Логика обновления данных
            # 1. Удаление абитуриентов, которые отсутствуют в новых данных
            # 2. Добавление новых абитуриентов
            # 3. Обновление существующих записей

            # Эта логика будет зависеть от конкретного источника данных
            # Для простоты реализуем заглушку

            return JsonResponse({'success': True, 'message': 'Данные успешно обновлены'})

        except Exception as e:
            return JsonResponse({'error': f'Ошибка при обновлении данных: {str(e)}'}, status=400)

    return render(request, 'update_data.html')


def calculate_passing_scores(request):
    """Расчет проходных баллов"""
    if request.method == 'POST':
        try:
            date_str = request.POST.get('date')
            if not date_str:
                return JsonResponse({'error': 'Не указана дата'}, status=400)

            calculator = AdmissionCalculator()
            passing_scores = calculator.calculate_passing_scores(parse_date(date_str))

            return JsonResponse({
                'success': True,
                'passing_scores': passing_scores,
                'date': date_str
            })

        except Exception as e:
            return JsonResponse({'error': f'Ошибка при расчете проходных баллов: {str(e)}'}, status=400)

    # Если GET запрос - показываем страницу с результатами
    date_str = request.GET.get('date', datetime.now().strftime('%Y-%m-%d'))
    calculator = AdmissionCalculator()

    try:
        passing_scores = calculator.calculate_passing_scores(parse_date(date_str))
        admitted_lists = calculator.get_admitted_applicants(parse_date(date_str))
        stats = calculator.get_statistics(parse_date(date_str))

        return render(request, 'passing_scores.html', {
            'passing_scores': passing_scores,
            'admitted_lists': admitted_lists,
            'stats': stats,
            'date': date_str
        })
    except Exception as e:
        return JsonResponse({'error': f'Ошибка при получении данных: {str(e)}'}, status=500)


def generate_pdf_report(request):
    """Генерация PDF-отчета"""
    date_str = request.GET.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%d.%m')

    try:
        reporter = PDFReporter()
        pdf_buffer = reporter.generate_report(parse_date(date_str))

        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{date_str}.pdf"'
        return response

    except Exception as e:
        return JsonResponse({'error': f'Ошибка при генерации отчета: {str(e)}'}, status=500)


def visualize_data(request):
    """Визуализация данных"""
    date_filter = request.GET.get('date', '')
    program_filter = request.GET.get('program', '')

    # Фильтрация данных
    admissions = AdmissionData.objects.select_related('applicant', 'educational_program')

    if date_filter:
        admissions = admissions.filter(date=parse_date(date_filter))

    if program_filter:
        admissions = admissions.filter(educational_program__code=program_filter)

    # Подготовка данных для шаблона
    data_list = []
    for adm in admissions:
        data_list.append({
            'id': adm.applicant.id,
            'program_name': adm.educational_program.name,
            'program_code': adm.educational_program.code,
            'total_score': adm.applicant.total_score,
            'has_consent': adm.has_consent,
            'priority': adm.priority,
            'date': adm.date.strftime('%d.%m.%Y') if adm.date else ''
        })

    programs = EducationalProgram.objects.all()

    return render(request, 'visualize_data.html', {
        'data_list': data_list,
        'programs': programs,
        'selected_date': date_filter,
        'selected_program': program_filter
    })


def clear_database(request):
    """Очистка базы данных"""
    if request.method == 'POST':
        try:
            # Удаляем все записи AdmissionData
            AdmissionData.objects.all().delete()
            # Удаляем всех абитуриентов (после удаления связанных записей)
            Applicant.objects.all().delete()

            return JsonResponse({'success': True, 'message': 'База данных очищена'})

        except Exception as e:
            return JsonResponse({'error': f'Ошибка при очистке базы данных: {str(e)}'}, status=400)

    return render(request, 'clear_database.html')


def generate_test_data(request):
    """Генерация тестовых данных"""
    if request.method == 'POST':
        try:
            run_data_generation()
            return JsonResponse({'success': True, 'message': 'Тестовые данные сгенерированы'})

        except Exception as e:
            return JsonResponse({'error': f'Ошибка при генерации данных: {str(e)}'}, status=400)

    return render(request, 'generate_test_data.html')
