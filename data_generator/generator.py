"""
Генератор конкурсных списков для приемной комиссии
Соответствует требованиям Московской предпрофессиональной олимпиады
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime
from typing import Dict, List, Tuple, Set
import json
import os

fake = Faker('ru_RU')
random.seed(42)  # Для воспроизводимости
np.random.seed(42)


class DataGenerator:
    def __init__(self):
        # Конфигурация согласно ТЗ
        self.programs = {
            'ПМ': {'name': 'Прикладная математика', 'capacity': 40, 'slug': 'pm'},
            'ИВТ': {'name': 'Информатика и вычислительная техника', 'capacity': 50, 'slug': 'ivt'},
            'ИТСС': {'name': 'Инфокоммуникационные технологии и системы связи', 'capacity': 30, 'slug': 'itss'},
            'ИБ': {'name': 'Информационная безопасность', 'capacity': 20, 'slug': 'ib'}
        }

        self.dates = ['01.08', '02.08', '03.08', '04.08']

        # Количество абитуриентов по дням и программам (из ТЗ п.8)
        self.program_counts = {
            '01.08': {'ПМ': 60, 'ИВТ': 100, 'ИТСС': 50, 'ИБ': 70},
            '02.08': {'ПМ': 380, 'ИВТ': 370, 'ИТСС': 350, 'ИБ': 260},
            '03.08': {'ПМ': 1000, 'ИВТ': 1150, 'ИТСС': 1050, 'ИБ': 800},
            '04.08': {'ПМ': 1240, 'ИВТ': 1390, 'ИТСС': 1240, 'ИБ': 1190}
        }

        # Пересечения для множества абитуриентов только двух ОП (из ТЗ п.9)
        self.intersections_2 = {
            '01.08': {
                ('ПМ', 'ИВТ'): 22, ('ПМ', 'ИТСС'): 17, ('ПМ', 'ИБ'): 20,
                ('ИВТ', 'ИТСС'): 19, ('ИВТ', 'ИБ'): 22, ('ИТСС', 'ИБ'): 17
            },
            '02.08': {
                ('ПМ', 'ИВТ'): 190, ('ПМ', 'ИТСС'): 190, ('ПМ', 'ИБ'): 150,
                ('ИВТ', 'ИТСС'): 190, ('ИВТ', 'ИБ'): 140, ('ИТСС', 'ИБ'): 120
            },
            # ... остальные дни по аналогии
        }

        # Глобальный словарь для хранения всех абитуриентов
        # Ключ: original_id, Значение: данные абитуриента
        self.all_applicants = {}

        # Счетчик для генерации ID
        self.next_id = 1

    def generate_applicant(self, applicant_id: int) -> Dict:
        """Генерация данных одного абитуриента"""
        # Генерация баллов (диапазоны можно настроить)
        physics_score = random.randint(40, 100)
        russian_score = random.randint(40, 100)
        math_score = random.randint(40, 100)
        achievement_score = random.randint(0, 10)
        total_score = physics_score + russian_score + math_score + achievement_score

        # Пока не генерируем согласие - это будет зависеть от программы и дня
        # Пока не назначаем программы - это будет в отдельных методах

        return {
            'id': applicant_id,
            'physics_score': physics_score,
            'russian_score': russian_score,
            'math_score': math_score,
            'achievement_score': achievement_score,
            'total_score': total_score,
            'has_consent': False,  # Будет установлено позже
            'applications': {}  # Будет хранить программы и приоритеты: {program: priority}
        }

    def generate_base_day(self, date: str) -> Dict[str, List[Dict]]:
        """
        Генерация базового дня (01.08)
        Возвращает словарь: программа -> список абитуриентов
        """
        print(f"Генерация базового дня {date}...")

        # Структура для хранения результатов
        day_data = {program: [] for program in self.programs}

        # TODO: Реализовать сложную логику пересечений
        # Пока создадим упрощенную версию для начала

        for program in self.programs:
            count = self.program_counts[date][program]
            for i in range(count):
                applicant_id = self.next_id
                applicant = self.generate_applicant(applicant_id)

                # Добавляем информацию о программе
                # В реальности здесь сложная логика пересечений
                applicant['applications'][program] = random.randint(1, 4)

                # На 01.08 согласий должно быть МЕНЬШЕ чем мест (для испытания №2)
                # Делаем случайно, но контролируем количество
                if random.random() < 0.3:  # 30% абитуриентов с согласием
                    applicant['has_consent'] = True

                day_data[program].append(applicant)
                self.all_applicants[applicant_id] = applicant
                self.next_id += 1

        print(f"Сгенерировано {sum(len(v) for v in day_data.values())} абитуриентов")
        return day_data

    def save_to_csv(self, day_data: Dict[str, List[Dict]], date: str):
        """Сохранение данных дня в CSV файлы"""
        os.makedirs('output', exist_ok=True)

        for program, applicants in day_data.items():
            # Преобразуем в DataFrame
            rows = []
            for applicant in applicants:
                row = {
                    'ID': applicant['id'],
                    'Согласие': 1 if applicant['has_consent'] else 0,
                    'Приоритет': applicant['applications'].get(program, 1),
                    'Балл_Физика/ИКТ': applicant['physics_score'],
                    'Балл_Русский': applicant['russian_score'],
                    'Балл_Математика': applicant['math_score'],
                    'Балл_ИД': applicant['achievement_score'],
                    'Сумма_баллов': applicant['total_score']
                }
                rows.append(row)

            df = pd.DataFrame(rows)
            filename = f"output/{self.programs[program]['slug']}_{date.replace('.', '_')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Сохранено: {filename} ({len(df)} записей)")

    def validate_counts(self, day_data: Dict[str, List[Dict]], date: str):
        """Проверка соответствия количества абитуриентов требованиям"""
        print(f"\nВалидация для {date}:")
        for program in self.programs:
            expected = self.program_counts[date][program]
            actual = len(day_data[program])
            status = "✓" if expected == actual else "✗"
            print(f"  {program}: {actual}/{expected} {status}")

    def generate_all(self):
        """Генерация всех дней"""
        print("=" * 50)
        print("ГЕНЕРАЦИЯ КОНКУРСНЫХ СПИСКОВ")
        print("=" * 50)

        for date in self.dates:
            day_data = self.generate_base_day(date)
            self.validate_counts(day_data, date)
            self.save_to_csv(day_data, date)
            print()


if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all()
    print("\nГенерация завершена!")
