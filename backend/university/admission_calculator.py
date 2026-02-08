from collections import defaultdict
from admission_api.models import Applicant, EducationalProgram, AdmissionData


class AdmissionCalculator:
    @staticmethod
    def calculate_passing_scores(date):
        """
        Рассчитывает проходные баллы для всех программ на определенную дату
        """
        programs = EducationalProgram.objects.all()
        passing_scores = {}

        for program in programs:
            # Получаем всех абитуриентов с согласием на зачисление для этой программы
            admitted_applicants = AdmissionData.objects.filter(
                educational_program=program,
                date=date,
                has_consent=True
            ).select_related('applicant')

            # Сортируем по баллам (по убыванию), затем по приоритету (по возрастанию)
            sorted_applicants = sorted(
                admitted_applicants,
                key=lambda x: (-x.applicant.total_score, x.priority)
            )

            # Если абитуриентов меньше мест, то проходной балл - НЕДОБОР
            if len(sorted_applicants) < program.seats:
                passing_scores[program.code] = "НЕДОБОР"
            else:
                # Проходной балл - балл последнего зачисленного абитуриента
                last_admitted = sorted_applicants[program.seats - 1]
                passing_scores[program.code] = last_admitted.applicant.total_score

        return passing_scores

    @staticmethod
    def get_admitted_applicants(date):
        """
        Получает список зачисленных абитуриентов для всех программ
        """
        programs = EducationalProgram.objects.all()
        admitted_lists = {}

        for program in programs:
            # Получаем всех абитуриентов с согласием на зачисление для этой программы
            admitted_applicants = AdmissionData.objects.filter(
                educational_program=program,
                date=date,
                has_consent=True
            ).select_related('applicant')

            # Сортируем по баллам (по убыванию), затем по приоритету (по возрастанию)
            sorted_applicants = sorted(
                admitted_applicants,
                key=lambda x: (-x.applicant.total_score, x.priority)
            )

            # Берем только тех, кто попадает в лимит мест
            admitted_for_program = sorted_applicants[:program.seats]

            # Формируем список ID и баллов
            admitted_info = [
                {
                    'id': applicant.applicant.id,
                    'total_score': applicant.applicant.total_score
                }
                for applicant in admitted_for_program
            ]

            admitted_lists[program.code] = admitted_info

        return admitted_lists

    @staticmethod
    def get_statistics(date):
        """
        Получает статистику по программам для отчета
        """
        programs = EducationalProgram.objects.all()
        statistics = {}

        for program in programs:
            # Все абитуриенты на программу
            all_applicants = AdmissionData.objects.filter(
                educational_program=program,
                date=date
            )

            # Абитуриенты с согласием
            consent_applicants = all_applicants.filter(has_consent=True)

            # Сортируем абитуриентов с согласием для определения зачисленных
            sorted_consents = sorted(
                consent_applicants,
                key=lambda x: (-x.applicant.total_score, x.priority)
            )

            admitted_count = min(len(sorted_consents), program.seats)
            admitted_applicants = sorted_consents[:admitted_count]

            # Статистика по приоритетам
            priority_counts = defaultdict(int)
            admitted_priority_counts = defaultdict(int)

            for applicant in all_applicants:
                priority_counts[applicant.priority] += 1

            for applicant in admitted_applicants:
                admitted_priority_counts[applicant.priority] += 1

            statistics[program.code] = {
                'total_applications': all_applicants.count(),
                'seats': program.seats,
                'first_priority': priority_counts[1],
                'second_priority': priority_counts[2],
                'third_priority': priority_counts[3],
                'fourth_priority': priority_counts[4],
                'admitted_first_priority': admitted_priority_counts[1],
                'admitted_second_priority': admitted_priority_counts[2],
                'admitted_third_priority': admitted_priority_counts[3],
                'admitted_fourth_priority': admitted_priority_counts[4]
            }

        return statistics
