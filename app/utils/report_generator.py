"""
Utility module for generating PDF reports
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from ..models import db, EducationalProgram, AdmissionData
from .calculator import calculate_passing_scores, get_statistics_for_date
import tempfile


def generate_pdf_report(report_date):
    """
    Generate a comprehensive PDF report with admission statistics
    """
    # Create temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    # Create document
    doc = SimpleDocTemplate(temp_filename, pagesize=A4)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=0
    )
    
    # Title
    title = Paragraph("Отчет о конкурсе на образовательные программы", title_style)
    elements.append(title)
    
    # Report generation info
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gen_info = Paragraph(f"Дата и время формирования отчета: {gen_time}", styles['Normal'])
    elements.append(gen_info)
    elements.append(Spacer(1, 12))
    
    # Passing scores section
    elements.append(Paragraph("Проходные баллы на образовательные программы:", heading_style))
    
    passing_scores = calculate_passing_scores(report_date)
    score_data = [['Программа', 'Код', 'Проходной балл']]
    
    for code, score_info in passing_scores.items():
        program = EducationalProgram.query.filter_by(code=code).first()
        if score_info['score'] == 'НЕДОБОР':
            score_display = 'НЕДОБОР'
        else:
            score_display = str(score_info['score'])
        
        score_data.append([
            program.name if program else code,
            code,
            score_display
        ])
    
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
    elements.append(Spacer(1, 20))
    
    # Statistics table
    elements.append(Paragraph("Статистика по образовательным программам:", heading_style))
    
    stats = get_statistics_for_date(report_date)
    stats_headers = [
        'Программа', 'Код', 'Всего заявлений', 'Мест', 
        'Заявления 1-го приоритета', 'Заявления 2-го приоритета', 
        'Заявления 3-го приоритета', 'Заявления 4-го приоритета',
        'Зачислено 1-го приоритета', 'Зачислено 2-го приоритета', 
        'Зачислено 3-го приоритета', 'Зачислено 4-го приоритета'
    ]
    
    stats_data = [stats_headers]
    
    for code, stat_info in stats.items():
        row = [
            stat_info['program_name'],
            code,
            stat_info['total_applications'],
            stat_info['budget_places'],
            stat_info['applications_by_priority'][1],
            stat_info['applications_by_priority'][2],
            stat_info['applications_by_priority'][3],
            stat_info['applications_by_priority'][4],
            stat_info['accepted_by_priority'][1],
            stat_info['accepted_by_priority'][2],
            stat_info['accepted_by_priority'][3],
            stat_info['accepted_by_priority'][4]
        ]
        stats_data.append(row)
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WRAP', (0, 0), (-1, -1), 'CJK')
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Accepted applicants for each program
    programs = EducationalProgram.query.all()
    for program in programs:
        elements.append(Paragraph(f"Список абитуриентов, зачисленных на программу '{program.name}' ({program.code}):", heading_style))
        
        # Get accepted applicants for this program
        passing_scores_for_date = calculate_passing_scores(report_date)
        if passing_scores_for_date[program.code]['score'] != 'НЕДОБОР':
            accepted_applicants = db.session.query(AdmissionData).filter(
                AdmissionData.date == report_date,
                AdmissionData.educational_program == program.code,
                AdmissionData.consent_given == True
            ).order_by(AdmissionData.total_score.desc()).limit(program.budget_places).all()
        else:
            # If shortage, get all applicants with consent
            accepted_applicants = db.session.query(AdmissionData).filter(
                AdmissionData.date == report_date,
                AdmissionData.educational_program == program.code,
                AdmissionData.consent_given == True
            ).order_by(AdmissionData.total_score.desc()).all()
        
        if accepted_applicants:
            applicants_data = [['ID абитуриента', 'Сумма баллов', 'Приоритет']]
            for app in accepted_applicants:
                applicants_data.append([str(app.applicant_id), str(app.total_score), str(app.priority_op)])
            
            applicants_table = Table(applicants_data)
            applicants_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(applicants_table)
        else:
            elements.append(Paragraph("Нет зачисленных абитуриентов.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
    
    # Build the PDF
    doc.build(elements)
    
    return temp_filename


def generate_dynamic_report(start_date, end_date):
    """
    Generate a dynamic report showing the dynamics of passing scores over time
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_filename = temp_file.name
    temp_file.close()
    
    doc = SimpleDocTemplate(temp_filename, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        alignment=0
    )
    
    # Title
    title = Paragraph("Динамика проходных баллов по образовательным программам", title_style)
    elements.append(title)
    
    # TODO: Add charts showing the dynamics of passing scores over time
    elements.append(Paragraph("Динамика проходных баллов (графики):", heading_style))
    elements.append(Paragraph("На этой странице должны отображаться графики динамики проходных баллов по программам за указанный период.", styles['Normal']))
    
    elements.append(Spacer(1, 20))
    
    # Detailed daily breakdown
    elements.append(Paragraph("Детальная информация по дням:", heading_style))
    
    # For simplicity, let's assume we're looking at the standard dates from the assignment
    standard_dates = ["2023-08-01", "2023-08-02", "2023-08-03", "2023-08-04"]
    
    for date_str in standard_dates:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        elements.append(Paragraph(f"Дата: {report_date.strftime('%d.%m.%Y')}", styles['Heading3']))
        
        daily_scores = calculate_passing_scores(report_date)
        daily_data = [['Программа', 'Код', 'Проходной балл']]
        
        for code, score_info in daily_scores.items():
            program = EducationalProgram.query.filter_by(code=code).first()
            if score_info['score'] == 'НЕДОБОР':
                score_display = 'НЕДОБОР'
            else:
                score_display = str(score_info['score'])
            
            daily_data.append([
                program.name if program else code,
                code,
                score_display
            ])
        
        daily_table = Table(daily_data)
        daily_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(daily_table)
        elements.append(Spacer(1, 15))
    
    doc.build(elements)
    
    return temp_filename