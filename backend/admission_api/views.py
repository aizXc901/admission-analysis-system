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
            # Получаем файлы из запроса
            uploaded_files = request.FILES.getlist('files')

            if not uploaded_files:
                return JsonResponse({'error': 'Не загружены файлы для обновления'}, status=400)

            all_records = []
            total_processed = 0

            # Обрабатываем каждый загруженный файл
            for uploaded_file in uploaded_files:
                # Определение типа файла
                if uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    return JsonResponse({'error': 'Неподдерживаемый формат файла'}, status=400)

                # Добавляем записи из файла в общий список
                for _, row in df.iterrows():
                    all_records.append(row)
                total_processed += len(df)

            # Получаем все существующие записи в базе данных
            existing_admissions = AdmissionData.objects.select_related('applicant', 'educational_program').all()
            
            # Создаем словарь существующих записей для быстрого поиска (ключ: (ID абитуриента, код программы))
            existing_map = {}
            for adm in existing_admissions:
                key = (adm.applicant.id, adm.educational_program.code)
                existing_map[key] = adm

            # Создаем словарь новых записей для быстрого поиска
            new_records_map = {}
            for row in all_records:
                key = (row['ID'], row['ОП'])
                new_records_map[key] = row

            # 1. Определяем абитуриентов, которых нужно удалить (есть в БД, но нет в новых данных)
            to_delete = []
            for key, adm in existing_map.items():
                if key not in new_records_map:
                    to_delete.append(adm)

            # 2. Определяем абитуриентов, которых нужно добавить (есть в новых данных, но нет в БД)
            to_add = []
            for key, row in new_records_map.items():
                if key not in existing_map:
                    to_add.append(row)

            # 3. Определяем абитуриентов, которых нужно обновить (есть и в БД, и в новых данных)
            to_update = []
            for key, row in new_records_map.items():
                if key in existing_map:
                    to_update.append((existing_map[key], row))

            # Выполняем операции с базой данных
            deleted_count = 0
            added_count = 0
            updated_count = 0

            # Удаляем записи
            for adm in to_delete:
                adm.delete()
                deleted_count += 1

            # Добавляем и обновляем записи
            for row in to_add:
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

                # Создаем новую запись в AdmissionData
                AdmissionData.objects.create(
                    applicant=applicant,
                    educational_program=program,
                    date=parse_date(row['Дата']) if 'Дата' in row else datetime.now().date(),
                    has_consent=bool(row['Наличие согласия о зачислении в ВУЗ']),
                    priority=int(row['Приоритет ОП'])
                )
                added_count += 1

            # Обновляем существующие записи
            for existing_adm, row in to_update:
                # Обновляем информацию об абитуриенте
                existing_adm.applicant.physics_ikt = row['Балл Физика/ИКТ']
                existing_adm.applicant.russian_lang = row['Балл Русский язык']
                existing_adm.applicant.math = row['Балл Математика']
                existing_adm.applicant.achievements = row['Балл за индивидуальные достижения']
                existing_adm.applicant.total_score = row['Сумма баллов']
                existing_adm.applicant.save()

                # Обновляем информацию в AdmissionData
                existing_adm.date = parse_date(row['Дата']) if 'Дата' in row else datetime.now().date()
                existing_adm.has_consent = bool(row['Наличие согласия о зачислении в ВУЗ'])
                existing_adm.priority = int(row['Приоритет ОП'])
                existing_adm.save()
                updated_count += 1

            return JsonResponse({
                'success': True, 
                'message': f'Данные успешно обновлены: добавлено {added_count}, обновлено {updated_count}, удалено {deleted_count}',
                'records_count': total_processed,
                'added_count': added_count,
                'updated_count': updated_count,
                'deleted_count': deleted_count
            })

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
