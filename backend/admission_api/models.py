from django.db import models

class EducationalProgram(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    seats = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Образовательная программа"
        verbose_name_plural = "Образовательные программы"


class Applicant(models.Model):
    id = models.AutoField(primary_key=True)
    physics_ikt = models.IntegerField(verbose_name="Балл Физика/ИКТ")
    russian_lang = models.IntegerField(verbose_name="Балл Русский язык")
    math = models.IntegerField(verbose_name="Балл Математика")
    achievements = models.IntegerField(verbose_name="Балл за индивидуальные достижения")
    total_score = models.IntegerField(verbose_name="Сумма баллов")

    def __str__(self):
        return f"Абитуриент #{self.id}"

    class Meta:
        verbose_name = "Абитуриент"
        verbose_name_plural = "Абитуриенты"


class AdmissionData(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, verbose_name="Абитуриент")
    educational_program = models.ForeignKey(EducationalProgram, on_delete=models.CASCADE, verbose_name="Образовательная программа")
    date = models.DateField(verbose_name="Дата")
    has_consent = models.BooleanField(verbose_name="Наличие согласия о зачислении")
    priority = models.IntegerField(verbose_name="Приоритет ОП", choices=[(i, i) for i in range(1, 5)])

    def __str__(self):
        return f"{self.applicant} - {self.educational_program} - {self.date}"

    class Meta:
        unique_together = ('applicant', 'educational_program', 'date')
        verbose_name = "Запись о поступлении"
        verbose_name_plural = "Записи о поступлении"
