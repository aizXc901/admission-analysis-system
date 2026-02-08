import random
import pandas as pd
from datetime import datetime
from admission_api.models import Applicant, EducationalProgram, AdmissionData


class DataGenerator:
    def __init__(self):
        self.programs = {
            'ПМ': {'name': 'Прикладная математика', 'seats': 40},
            'ИВТ': {'name': 'Информатика и вычислительная техника', 'seats': 50},
            'ИТСС': {'name': 'Инфокоммуникационные технологии и системы связи', 'seats': 30},
            'ИБ': {'name': 'Информационная безопасность', 'seats': 20}
        }

        # Требуемые количества абитуриентов по датам
        self.required_counts = {
            '01.08': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
            '02.08': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
            '03.08': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
            '04.08': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190}
        }

        # Пересечения по двум программам
        self.pair_intersections = {
            '01.08': {'ПМ-ИВТ': 22, 'ПМ-ИТСС': 17, 'ПМ-ИБ': 20, 'ИВТ-ИТСС': 19, 'ИВТ-ИБ': 22, 'ИТСС-ИБ': 17},
            '02.08': {'ПМ-ИВТ': 190, 'ПМ-ИТСС': 190, 'ПМ-ИБ': 150, 'ИВТ-ИТСС': 190, 'ИВТ-ИБ': 140, 'ИТСС-ИБ': 120},
            '03.08': {'ПМ-ИВТ': 760, 'ПМ-ИТСС': 600, 'ПМ-ИБ': 410, 'ИВТ-ИТСС': 750, 'ИВТ-ИБ': 460, 'ИТСС-ИБ': 500},
            '04.08': {'ПМ-ИВТ': 1090, 'ПМ-ИТСС': 1110, 'ПМ-ИБ': 1070, 'ИВТ-ИТСС': 1050, 'ИВТ-ИБ': 1040, 'ИТСС-ИБ': 1090}
        }

        # Пересечения по трем/четырем программам
        self.multi_intersections = {
            '01.08': {'ПМ-ИВТ-ИТСС': 5, 'ПМ-ИВТ-ИБ': 5, 'ИВТ-ИТСС-ИБ': 5, 'ПМ-ИТСС-ИБ': 5, 'ПМ-ИВТ-ИТСС-ИБ': 3},
            '02.08': {'ПМ-ИВТ-ИТСС': 70, 'ПМ-ИВТ-ИБ': 70, 'ИВТ-ИТСС-ИБ': 70, 'ПМ-ИТСС-ИБ': 70, 'ПМ-ИВТ-ИТСС-ИБ': 50},
            '03.08': {'ПМ-ИВТ-ИТСС': 500, 'ПМ-ИВТ-ИБ': 260, 'ИВТ-ИТСС-ИБ': 300, 'ПМ-ИТСС-ИБ': 250,
                      'ПМ-ИВТ-ИТСС-ИБ': 200},
            '04.08': {'ПМ-ИВТ-ИТСС': 1020, 'ПМ-ИВТ-ИБ': 1020, 'ИВТ-ИТСС-ИБ': 1000, 'ПМ-ИТСС-ИБ': 1040,
                      'ПМ-ИВТ-ИТСС-ИБ': 1000}
        }

    def generate_applicant_data(self, applicant_id, date):
        """Генерирует данные для одного абитуриента"""
        physics_ikt = random.randint(0, 100)
        russian_lang = random.randint(0, 100)
        math = random.randint(0, 100)
        achievements = random.randint(0, 10)
        total_score = physics_ikt + russian_lang + math + achievements

        # С вероятностью 70% абитуриент имеет согласие
        has_consent = random.random() < 0.7

        # Приоритеты - от 1 до 4
        priority = random.randint(1, 4)

        return {
            'id': applicant_id,
            'has_consent': has_consent,
            'priority': priority,
            'physics_ikt': physics_ikt,
            'russian_lang': russian_lang,
            'math': math,
            'achievements': achievements,
            'total_score': total_score
        }

    def generate_date_data(self, date):
        """Генерирует данные для одной даты"""
        applicants_data = []
        used_ids = set()

        # Сначала генерируем уникальные ID для пересечений
        total_applicants = sum(self.required_counts[date].values())

        # Учитываем пересечения
        all_applicant_ids = set(range(1, total_applicants + 100))  # немного больше для пересечений

        # Генерируем абитуриентов для каждой программы
        for program_code, required_count in self.required_counts[date].items():
            program_applicants = []

            # Сначала добавляем абитуриентов с пересечениями
            # Пересечения по двум программам
            for pair_key, intersection_count in self.pair_intersections[date].items():
                if program_code in pair_key:
                    other_program = None
                    for p in ['ПМ', 'ИВТ', 'ИТСС', 'ИБ']:
                        if p != program_code and p in pair_key:
                            other_program = p
                            break
                    if other_program:
                        # Выбираем ID для пересечения
                        available_ids = list(all_applicant_ids - used_ids)
                        selected_ids = random.sample(available_ids, min(intersection_count, len(available_ids)))
                        used_ids.update(selected_ids)

                        for aid in selected_ids:
                            data = self.generate_applicant_data(aid, date)
                            program_applicants.append((aid, data))

            # Пересечения по трем/четырем программам
            for multi_key, intersection_count in self.multi_intersections[date].items():
                if program_code in multi_key:
                    # Выбираем ID для многопрограммного пересечения
                    available_ids = list(all_applicant_ids - used_ids)
                    selected_ids = random.sample(available_ids, min(intersection_count, len(available_ids)))
                    used_ids.update(selected_ids)

                    for aid in selected_ids:
                        data = self.generate_applicant_data(aid, date)
                        program_applicants.append((aid, data))

            # Добавляем остальных абитуриентов до нужного количества
            current_count = len(program_applicants)
            needed_count = required_count - current_count

            if needed_count > 0:
                available_ids = list(all_applicant_ids - used_ids)
                selected_ids = random.sample(available_ids[:needed_count],
                                             min(needed_count, len(available_ids[:needed_count])))
                used_ids.update(selected_ids)

                for aid in selected_ids:
                    data = self.generate_applicant_data(aid, date)
                    program_applicants.append((aid, data))

            # Сохраняем данные для этой программы и даты
            applicants_data.extend(program_applicants)

        return applicants_data

    def save_to_database(self, date, applicants_data, program_code):
        """Сохраняет данные в базу данных"""
        for applicant_id, data in applicants_data:
            # Получаем или создаем абитуриента
            applicant, created = Applicant.objects.get_or_create(
                id=applicant_id,
                defaults={
                    'physics_ikt': data['physics_ikt'],
                    'russian_lang': data['russian_lang'],
                    'math': data['math'],
                    'achievements': data['achievements'],
                    'total_score': data['total_score']
                }
            )

            # Получаем программу
            program = EducationalProgram.objects.get(code=program_code)

            # Создаем или обновляем запись в AdmissionData
            admission_data, created = AdmissionData.objects.get_or_create(
                applicant=applicant,
                educational_program=program,
                defaults={
                    'date': datetime.strptime(date, '%d.%m').date() if '.' in date else datetime.now().date(),
                    'has_consent': data['has_consent'],
                    'priority': data['priority']
                }
            )

            if not created:
                # Обновляем существующую запись
                admission_data.has_consent = data['has_consent']
                admission_data.priority = data['priority']
                admission_data.save()

    def generate_all_data(self):
        """Генерирует все тестовые данные для всех дат"""
        dates = ['01.08', '02.08', '03.08', '04.08']

        for date in dates:
            for program_code in self.programs.keys():
                print(f"Генерация данных для {date}, программа {program_code}...")
                applicants_data = self.generate_date_data(date)
                # Фильтруем данные только для текущей программы
                program_applicants = []
                for aid, data in applicants_data:
                    if aid not in [item[0] for item in program_applicants]:
                        # Просто добавляем абитуриента к программе, используя случайный приоритет
                        data_copy = data.copy()
                        data_copy['priority'] = random.randint(1, 4)
                        program_applicants.append((aid, data_copy))

                self.save_to_database(date, program_applicants, program_code)
                print(f"Сгенерировано {len(program_applicants)} записей для {date}, программа {program_code}")


# Функция для запуска генерации данных
def run_data_generation():
    generator = DataGenerator()
    generator.generate_all_data()
    print("Генерация данных завершена!")
