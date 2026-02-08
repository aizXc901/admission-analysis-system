from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import base64
from .admission_calculator import AdmissionCalculator


class PDFReporter:
    def __init__(self):
        self.calculator = AdmissionCalculator()

    def generate_report(self, date):
        """
        Генерирует PDF-отчет для определенной даты
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Заголовок отчета
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
        )
        title = Paragraph(f'Отчет о приемной кампании от {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}', title_style)
        elements.append(title)

        # Проходные баллы
        passing_scores = self.calculator.calculate_passing_scores(date)
        elements.append(Paragraph('Проходные баллы на образовательные программы:', styles['Heading2']))

        score_data = [['Программа', 'Проходной балл']]
        for code, score in passing_scores.items():
            program_names = {
                'ПМ': 'Прикладная математика',
                'ИВТ': 'Информатика и вычислительная техника',
                'ИТСС': 'Инфокоммуникационные технологии и системы связи',
                'ИБ': 'Информационная безопасность'
            }
            score_data.append([program_names[code], str(score)])

        score_table = Table(score_data)
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 12))

        # График динамики проходных баллов (если есть данные за другие даты)
        try:
            # Попробуем получить данные за все даты для графика
            all_dates = ['01.08', '02.08', '03.08', '04.08']
            program_codes = ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']

            fig, ax = plt.subplots(figsize=(10, 6))

            for program in program_codes:
                scores_over_time = []
                for d in all_dates:
                    try:
                        scores = self.calculator.calculate_passing_scores(d)
                        score = scores[program]
                        if isinstance(score, str) and score == "НЕДОБОР":
                            scores_over_time.append(0)  # Временное значение для НЕДОБОРА
                        else:
                            scores_over_time.append(score)
                    except:
                        scores_over_time.append(0)

                ax.plot(all_dates, scores_over_time, marker='o', label=program)

            ax.set_xlabel('Дата')
            ax.set_ylabel('Проходной балл')
            ax.set_title('Динамика проходных баллов по образовательным программам')
            ax.legend()
            ax.grid(True)

            # Сохраняем график во временный буфер
            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            plt.close()

            elements.append(Spacer(1, 12))
        except:
            # Если не удалось создать график, просто пропускаем
            pass

        # Списки зачисленных абитуриентов
        admitted_lists = self.calculator.get_admitted_applicants(date)
        elements.append(Paragraph('Списки зачисленных абитуриентов:', styles['Heading2']))

        for program_code, admitted in admitted_lists.items():
            program_names = {
                'ПМ': 'Прикладная математика',
                'ИВТ': 'Информатика и вычислительная техника',
                'ИТСС': 'Инфокоммуникационные технологии и системы связи',
                'ИБ': 'Информационная безопасность'
            }

            elements.append(Paragraph(f'{program_names[program_code]}:', styles['Heading3']))

            if admitted:
                admitted_data = [['ID', 'Сумма баллов']]
                for applicant in admitted:
                    admitted_data.append([str(applicant['id']), str(applicant['total_score'])])

                admitted_table = Table(admitted_data)
                admitted_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(admitted_table)
            else:
                elements.append(Paragraph('Нет зачисленных абитуриентов.', styles['Normal']))

            elements.append(Spacer(1, 12))

        # Статистика по программам
        stats = self.calculator.get_statistics(date)
        elements.append(Paragraph('Статистика по образовательным программам:', styles['Heading2']))

        stat_headers = [
            '', 'ПМ', 'ИВТ', 'ИТСС', 'ИБ'
        ]

        stat_rows = [
            ['Общее кол-во заявлений'],
            ['Количество мест на ОП', '40', '50', '30', '20'],
            ['Кол-во заявлений 1-го приоритета'],
            ['Кол-во заявлений 2-го приоритета'],
            ['Кол-во заявлений 3-го приоритета'],
            ['Кол-во заявлений 4-го приоритета'],
            ['Кол-во зачисленных 1-го приоритета'],
            ['Кол-во зачисленных 2-го приоритета'],
            ['Кол-во зачисленных 3-го приоритета'],
            ['Кол-во зачисленных 4-го приоритета']
        ]

        # Заполняем статистику
        for i, row in enumerate(stat_rows):
            if i == 0:  # Общее количество заявлений
                row.extend([
                    str(stats['ПМ']['total_applications']),
                    str(stats['ИВТ']['total_applications']),
                    str(stats['ИТСС']['total_applications']),
                    str(stats['ИБ']['total_applications'])
                ])
            elif i == 2:  # Заявления 1-го приоритета
                row.extend([
                    str(stats['ПМ']['first_priority']),
                    str(stats['ИВТ']['first_priority']),
                    str(stats['ИТСС']['first_priority']),
                    str(stats['ИБ']['first_priority'])
                ])
            elif i == 3:  # Заявления 2-го приоритета
                row.extend([
                    str(stats['ПМ']['second_priority']),
                    str(stats['ИВТ']['second_priority']),
                    str(stats['ИТСС']['second_priority']),
                    str(stats['ИБ']['second_priority'])
                ])
            elif i == 4:  # Заявления 3-го приоритета
                row.extend([
                    str(stats['ПМ']['third_priority']),
                    str(stats['ИВТ']['third_priority']),
                    str(stats['ИТСС']['third_priority']),
                    str(stats['ИБ']['third_priority'])
                ])
            elif i == 5:  # Заявления 4-го приоритета
                row.extend([
                    str(stats['ПМ']['fourth_priority']),
                    str(stats['ИВТ']['fourth_priority']),
                    str(stats['ИТСС']['fourth_priority']),
                    str(stats['ИБ']['fourth_priority'])
                ])
            elif i == 6:  # Зачисленные 1-го приоритета
                row.extend([
                    str(stats['ПМ']['admitted_first_priority']),
                    str(stats['ИВТ']['admitted_first_priority']),
                    str(stats['ИТСС']['admitted_first_priority']),
                    str(stats['ИБ']['admitted_first_priority'])
                ])
            elif i == 7:  # Зачисленные 2-го приоритета
                row.extend([
                    str(stats['ПМ']['admitted_second_priority']),
                    str(stats['ИВТ']['admitted_second_priority']),
                    str(stats['ИТСС']['admitted_second_priority']),
                    str(stats['ИБ']['admitted_second_priority'])
                ])
            elif i == 8:  # Зачисленные 3-го приоритета
                row.extend([
                    str(stats['ПМ']['admitted_third_priority']),
                    str(stats['ИВТ']['admitted_third_priority']),
                    str(stats['ИТСС']['admitted_third_priority']),
                    str(stats['ИБ']['admitted_third_priority'])
                ])
            elif i == 9:  # Зачисленные 4-го приоритета
                row.extend([
                    str(stats['ПМ']['admitted_fourth_priority']),
                    str(stats['ИВТ']['admitted_fourth_priority']),
                    str(stats['ИТСС']['admitted_fourth_priority']),
                    str(stats['ИБ']['admitted_fourth_priority'])
                ])

        # Создаем таблицу со статистикой
        stat_data = [stat_headers]
        for row in stat_rows:
            stat_data.append(row)

        stat_table = Table(stat_data)
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(stat_table)

        # Собираем документ
        doc.build(elements)
        buffer.seek(0)

        return buffer
