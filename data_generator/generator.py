"""
Генератор конкурсных списков для приемной комиссии
Соответствует требованиям Московской предпрофессиональной олимпиады
"""
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime
from typing import Dict, List, Tuple, Set, Any
import json
import os
from collections import defaultdict, Counter
import itertools

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

        self.program_list = list(self.programs.keys())

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
            '03.08': {
                ('ПМ', 'ИВТ'): 760, ('ПМ', 'ИТСС'): 600, ('ПМ', 'ИБ'): 410,
                ('ИВТ', 'ИТСС'): 750, ('ИВТ', 'ИБ'): 460, ('ИТСС', 'ИБ'): 500
            },
            '04.08': {
                ('ПМ', 'ИВТ'): 1090, ('ПМ', 'ИТСС'): 1110, ('ПМ', 'ИБ'): 1070,
                ('ИВТ', 'ИТСС'): 1050, ('ИВТ', 'ИБ'): 1040, ('ИТСС', 'ИБ'): 1090
            }
        }

        # Пересечения для трех и четырех ОП (из ТЗ п.9)
        self.intersections_3_4 = {
            '01.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 5,
                ('ПМ', 'ИВТ', 'ИБ'): 5,
                ('ИВТ', 'ИТСС', 'ИБ'): 5,
                ('ПМ', 'ИТСС', 'ИБ'): 5,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 3
            },
            '02.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 70,
                ('ПМ', 'ИВТ', 'ИБ'): 70,
                ('ИВТ', 'ИТСС', 'ИБ'): 70,
                ('ПМ', 'ИТСС', 'ИБ'): 70,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 50
            },
            '03.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 500,
                ('ПМ', 'ИВТ', 'ИБ'): 260,
                ('ИВТ', 'ИТСС', 'ИБ'): 300,
                ('ПМ', 'ИТСС', 'ИБ'): 250,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 200
            },
            '04.08': {
                ('ПМ', 'ИВТ', 'ИТСС'): 1020,
                ('ПМ', 'ИВТ', 'ИБ'): 1020,
                ('ИВТ', 'ИТСС', 'ИБ'): 1000,
                ('ПМ', 'ИТСС', 'ИБ'): 1040,
                ('ПМ', 'ИВТ', 'ИТСС', 'ИБ'): 1000
            }
        }

        # Глобальный словарь для хранения всех абитуриентов
        # Ключ: original_id, Значение: данные абитуриента
        self.all_applicants = {}

        # Счетчик для генерации ID
        self.next_id = 1

        # Для отслеживания пересечений между днями
        self.day_applicants = {}  # date -> set(applicant_ids)

    def generate_applicant(self, applicant_id: int) -> Dict:
        """Генерация данных одного абитуриента"""
        # Генерация баллов с разными распределениями для реалистичности
        physics_score = random.choices(
            [random.randint(40, 60), random.randint(61, 80), random.randint(81, 100)],
            weights=[0.3, 0.5, 0.2]
        )[0]

        russian_score = random.choices(
            [random.randint(50, 70), random.randint(71, 90), random.randint(91, 100)],
            weights=[0.2, 0.5, 0.3]
        )[0]

        math_score = random.choices(
            [random.randint(45, 65), random.randint(66, 85), random.randint(86, 100)],
            weights=[0.3, 0.4, 0.3]
        )[0]

        achievement_score = random.choices(
            [0, 1, 2, 3, 5, 10],
            weights=[0.3, 0.2, 0.2, 0.15, 0.1, 0.05]
        )[0]

        total_score = physics_score + russian_score + math_score + achievement_score

        return {
            'id': applicant_id,
            'physics_score': physics_score,
            'russian_score': russian_score,
            'math_score': math_score,
            'achievement_score': achievement_score,
            'total_score': total_score,
            'has_consent': False,  # Будет установлено позже
            'applications': {},  # Будет хранить программы и приоритеты: {program: priority}
            'active_date': None  # Дата, когда абитуриент активен
        }

    def assign_priorities(self, programs: List[str]) -> Dict[str, int]:
        """Назначение приоритетов программам"""
        shuffled = programs.copy()
        random.shuffle(shuffled)
        priorities = {}
        for i, program in enumerate(shuffled, 1):
            priorities[program] = i
        return priorities

    def generate_day_with_intersections(self, date: str) -> Dict[str, List[Dict]]:
        """
        Генерация дня со сложными пересечениями
        Алгоритм:
        1. Сначала создаем абитуриентов, которые участвуют во всех 4 программах
        2. Затем для каждой комбинации из 3 программ
        3. Затем для каждой пары программ
        4. Остальных делаем уникальными для каждой программы
        """
        print(f"\nГенерация дня {date} со сложными пересечениями...")

        # Инициализируем структуры для хранения
        day_data = {program: [] for program in self.programs}
        applicant_programs = {}  # applicant_id -> list of programs

        # Шаг 1: Абитуриенты, участвующие во всех 4 программах
        count_4 = self.intersections_3_4[date][('ПМ', 'ИВТ', 'ИТСС', 'ИБ')]
        print(f"  Создаем {count_4} абитуриентов для всех 4 программ...")

        for _ in range(count_4):
            applicant = self.generate_applicant(self.next_id)
            all_programs = self.program_list.copy()
            applicant['applications'] = self.assign_priorities(all_programs)

            for program in all_programs:
                day_data[program].append(applicant)

            self.all_applicants[self.next_id] = applicant
            applicant_programs[self.next_id] = all_programs
            self.next_id += 1

        # Шаг 2: Абитуриенты для комбинаций из 3 программ
        three_program_combinations = [
            ('ПМ', 'ИВТ', 'ИТСС'),
            ('ПМ', 'ИВТ', 'ИБ'),
            ('ИВТ', 'ИТСС', 'ИБ'),
            ('ПМ', 'ИТСС', 'ИБ')
        ]

        for combo in three_program_combinations:
            count = self.intersections_3_4[date][combo]
            print(f"  Создаем {count} абитуриентов для программ {combo}...")

            for _ in range(count):
                applicant = self.generate_applicant(self.next_id)
                programs = list(combo)
                applicant['applications'] = self.assign_priorities(programs)

                for program in programs:
                    day_data[program].append(applicant)

                self.all_applicants[self.next_id] = applicant
                applicant_programs[self.next_id] = programs
                self.next_id += 1

        # Шаг 3: Абитуриенты для пар программ
        for (prog1, prog2), count in self.intersections_2[date].items():
            print(f"  Создаем {count} абитуриентов для пары ({prog1}, {prog2})...")

            for _ in range(count):
                applicant = self.generate_applicant(self.next_id)
                programs = [prog1, prog2]
                applicant['applications'] = self.assign_priorities(programs)

                for program in programs:
                    day_data[program].append(applicant)

                self.all_applicants[self.next_id] = applicant
                applicant_programs[self.next_id] = programs
                self.next_id += 1

        # Шаг 4: Уникальные абитуриенты для каждой программы
        print("  Добавляем уникальных абитуриентов...")

        for program in self.programs:
            # Сколько уже добавлено на эту программу
            current_count = len(day_data[program])
            target_count = self.program_counts[date][program]
            needed = target_count - current_count

            if needed > 0:
                for _ in range(needed):
                    applicant = self.generate_applicant(self.next_id)
                    programs = [program]
                    applicant['applications'] = {program: 1}

                    day_data[program].append(applicant)
                    self.all_applicants[self.next_id] = applicant
                    applicant_programs[self.next_id] = programs
                    self.next_id += 1

        # Сохраняем список абитуриентов дня
        self.day_applicants[date] = set(applicant_programs.keys())

        return day_data

    def update_day_from_previous(self, current_date: str, prev_date: str) -> Dict[str, List[Dict]]:
        """
        Генерация нового дня на основе предыдущего с обновлениями
        Соответствует пункту 2.10 ТЗ:
        - Удаление 5-10% записей
        - Добавление не менее 10% новых
        - Обновление остальных записей
        """
        print(f"\nГенерация дня {current_date} на основе {prev_date}...")

        # Получаем абитуриентов предыдущего дня
        prev_applicant_ids = self.day_applicants.get(prev_date, set())

        # Определяем сколько удалить (5-10%)
        delete_percent = random.uniform(0.05, 0.10)
        delete_count = int(len(prev_applicant_ids) * delete_percent)
        to_delete = set(random.sample(list(prev_applicant_ids), delete_count))

        # Определяем сколько добавить (не менее 10%)
        add_percent = random.uniform(0.10, 0.15)
        add_count = max(int(len(prev_applicant_ids) * add_percent), len(prev_applicant_ids) // 10)

        print(f"  Удаляем: {delete_count} абитуриентов ({delete_percent:.1%})")
        print(f"  Добавляем: {add_count} новых абитуриентов ({add_percent:.1%})")

        # Оставляем абитуриентов для обновления
        to_update = prev_applicant_ids - to_delete

        # Создаем структуру для нового дня
        day_data = {program: [] for program in self.programs}
        current_applicant_ids = set()

        # 1. Обновляем существующих абитуриентов
        for app_id in to_update:
            applicant = self.all_applicants[app_id].copy()

            # Обновляем баллы (немного меняем)
            for subject in ['physics_score', 'russian_score', 'math_score']:
                change = random.randint(-5, 5)
                applicant[subject] = max(0, min(100, applicant[subject] + change))

            # Может измениться балл ИД
            if random.random() < 0.1:
                applicant['achievement_score'] = random.randint(0, 10)

            applicant['total_score'] = (
                applicant['physics_score'] +
                applicant['russian_score'] +
                applicant['math_score'] +
                applicant['achievement_score']
            )

            # Может измениться согласие (особенно к 04.08)
            if current_date == '04.08' and random.random() < 0.7:
                applicant['has_consent'] = True
            elif random.random() < 0.2:
                applicant['has_consent'] = not applicant['has_consent']

            # Может измениться приоритет (редко)
            if random.random() < 0.05:
                programs = list(applicant['applications'].keys())
                if len(programs) > 1:
                    applicant['applications'] = self.assign_priorities(programs)

            applicant['active_date'] = current_date

            # Добавляем в соответствующие программы
            for program in applicant['applications']:
                day_data[program].append(applicant)

            current_applicant_ids.add(app_id)
            self.all_applicants[app_id] = applicant

        # 2. Добавляем новых абитуриентов
        for _ in range(add_count):
            applicant = self.generate_applicant(self.next_id)

            # Определяем на сколько программ подает абитуриент (1-4)
            num_programs = random.choices([1, 2, 3, 4], weights=[0.3, 0.3, 0.2, 0.2])[0]

            # Выбираем программы
            if num_programs == 1:
                programs = [random.choice(self.program_list)]
            elif num_programs == 4:
                programs = self.program_list.copy()
            else:
                programs = random.sample(self.program_list, num_programs)

            # Назначаем приоритеты
            applicant['applications'] = self.assign_priorities(programs)

            # Настраиваем согласие
            if current_date == '04.08':
                # На 04.08 много согласий
                applicant['has_consent'] = random.random() < 0.8
            else:
                applicant['has_consent'] = random.random() < 0.3

            applicant['active_date'] = current_date

            # Добавляем в соответствующие программы
            for program in programs:
                day_data[program].append(applicant)

            self.all_applicants[self.next_id] = applicant
            current_applicant_ids.add(self.next_id)
            self.next_id += 1

        # Сохраняем список абитуриентов дня
        self.day_applicants[current_date] = current_applicant_ids

        return day_data

    def adjust_for_final_day(self, day_data: Dict[str, List[Dict]]):
        """
        Корректировка данных для 04.08 согласно испытанию №2:
        1. Количество согласий > количества мест на каждой программе
        2. Проходные баллы должны быть: ПМ > ИБ > ИВТ > ИТСС
        """
        print("\nКорректировка данных для 04.08...")

        # 1. Убедимся, что согласий больше чем мест
        for program in self.programs:
            applicants = day_data[program]
            consent_count = sum(1 for a in applicants if a['has_consent'])
            capacity = self.programs[program]['capacity']

            if consent_count <= capacity:
                # Добавляем согласия лучшим абитуриентам
                sorted_apps = sorted(applicants, key=lambda x: x['total_score'], reverse=True)
                needed = capacity + random.randint(5, 15) - consent_count

                for i in range(min(needed, len(sorted_apps))):
                    if not sorted_apps[i]['has_consent']:
                        sorted_apps[i]['has_consent'] = True
                        # Обновляем в основном словаре
                        app_id = sorted_apps[i]['id']
                        if app_id in self.all_applicants:
                            self.all_applicants[app_id]['has_consent'] = True

                new_consent = sum(1 for a in applicants if a['has_consent'])
                print(f"  {program}: согласий {consent_count} -> {new_consent} (мест: {capacity})")

        # 2. Настроим баллы для нужного порядка проходных баллов
        # Для простоты скорректируем баллы у топ-абитуриентов

        # Соберем всех абитуриентов с согласием по программам
        program_top_applicants = {}
        for program in self.programs:
            applicants = [a for a in day_data[program] if a['has_consent']]
            sorted_apps = sorted(applicants, key=lambda x: x['total_score'], reverse=True)
            program_top_applicants[program] = sorted_apps[:self.programs[program]['capacity'] + 10]

        # Немного увеличим баллы у топовых на ПМ и ИБ
        # и уменьшим у ИВТ и ИТСС для создания нужного порядка
        adjustments = {
            'ПМ': +15,  # Самые высокие баллы
            'ИБ': +10,  # Чуть ниже ПМ
            'ИВТ': 0,   # Средние
            'ИТСС': -5  # Самые низкие
        }

        for program, adjustment in adjustments.items():
            if adjustment != 0:
                for applicant in program_top_applicants[program][:30]:  # Только топовые
                    app_id = applicant['id']
                    if app_id in self.all_applicants:
                        # Увеличиваем все баллы пропорционально
                        self.all_applicants[app_id]['physics_score'] = min(100,
                            self.all_applicants[app_id]['physics_score'] + adjustment//3)
                        self.all_applicants[app_id]['math_score'] = min(100,
                            self.all_applicants[app_id]['math_score'] + adjustment//3)
                        self.all_applicants[app_id]['total_score'] = (
                            self.all_applicants[app_id]['physics_score'] +
                            self.all_applicants[app_id]['russian_score'] +
                            self.all_applicants[app_id]['math_score'] +
                            self.all_applicants[app_id]['achievement_score']
                        )

        print("  Корректировка баллов завершена")

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
            print(f"    Сохранено: {filename} ({len(df)} записей)")

    def validate_counts(self, day_data: Dict[str, List[Dict]], date: str):
        """Проверка соответствия количества абитуриентов требованиям"""
        print(f"\nВалидация для {date}:")

        # Проверка общего количества
        for program in self.programs:
            expected = self.program_counts[date][program]
            actual = len(day_data[program])
            status = "✓" if expected == actual else "✗"
            print(f"  {program}: {actual}/{expected} {status}")

        # Проверка согласий (только для 04.08)
        if date == '04.08':
            print("\n  Проверка согласий на 04.08:")
            for program in self.programs:
                applicants = day_data[program]
                consent_count = sum(1 for a in applicants if a['has_consent'])
                capacity = self.programs[program]['capacity']
                status = "✓" if consent_count > capacity else "✗"
                print(f"    {program}: {consent_count} согласий > {capacity} мест {status}")

    def calculate_passing_scores(self, day_data: Dict[str, List[Dict]]):
        """Расчет проходных баллов (упрощенный) для проверки"""
        print("\n  Расчет проходных баллов (упрощенный):")

        for program in self.programs:
            # Берем только абитуриентов с согласием
            applicants = [a for a in day_data[program] if a['has_consent']]

            if not applicants:
                print(f"    {program}: НЕТ АБИТУРИЕНТОВ С СОГЛАСИЕМ")
                continue

            # Сортируем по убыванию баллов
            sorted_apps = sorted(applicants, key=lambda x: x['total_score'], reverse=True)

            capacity = self.programs[program]['capacity']

            if len(sorted_apps) <= capacity:
                print(f"    {program}: НЕДОБОР (только {len(sorted_apps)} с согласием)")
            else:
                passing_score = sorted_apps[capacity - 1]['total_score']
                print(f"    {program}: проходной балл ≈ {passing_score}")

    def generate_all(self):
        """Генерация всех дней"""
        print("=" * 60)
        print("ГЕНЕРАЦИЯ КОНКУРСНЫХ СПИСКОВ ДЛЯ ПРИЕМНОЙ КОМИССИИ")
        print("=" * 60)

        # Генерация базового дня (01.08)
        day_data_01 = self.generate_day_with_intersections('01.08')
        self.validate_counts(day_data_01, '01.08')
        self.calculate_passing_scores(day_data_01)
        self.save_to_csv(day_data_01, '01.08')

        # Генерация последующих дней с обновлениями
        day_data_prev = day_data_01

        for i, date in enumerate(self.dates[1:], 1):
            prev_date = self.dates[i-1]

            if date == '04.08':
                # Для 04.08 нужна особая обработка
                day_data = self.update_day_from_previous(date, prev_date)
                self.adjust_for_final_day(day_data)
            else:
                day_data = self.update_day_from_previous(date, prev_date)

            self.validate_counts(day_data, date)
            self.calculate_passing_scores(day_data)
            self.save_to_csv(day_data, date)
            day_data_prev = day_data

        # Сохраняем метаданные
        self.save_metadata()

        print("\n" + "=" * 60)
        print("ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 60)

    def save_metadata(self):
        """Сохранение метаданных для отладки"""
        metadata = {
            'total_applicants_generated': len(self.all_applicants),
            'day_applicant_counts': {date: len(ids) for date, ids in self.day_applicants.items()},
            'program_capacities': {p: self.programs[p]['capacity'] for p in self.programs}
        }

        with open('output/metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print("\nМетаданные сохранены в output/metadata.json")


if __name__ == "__main__":
    generator = DataGenerator()
    generator.generate_all()
