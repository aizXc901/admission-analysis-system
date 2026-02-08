from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class EducationalProgram(models.Model):
    """Образовательная программа (ОП)"""
    name = models.CharField('Название', max_length=100)
    code = models.CharField('Код', max_length=10, unique=True)
    slug = models.SlugField('Slug', max_length=10, unique=True)
    capacity = models.PositiveIntegerField('Количество бюджетных мест')
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Образовательная программа'
        verbose_name_plural = 'Образовательные программы'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.capacity} мест)"


class Applicant(models.Model):
    """Абитуриент"""
    original_id = models.IntegerField('ID из конкурсного списка', db_index=True)
    full_name = models.CharField('ФИО', max_length=200, blank=True)
    physics_score = models.IntegerField('Балл Физика/ИКТ', validators=[MinValueValidator(0), MaxValueValidator(100)])
    russian_score = models.IntegerField('Балл Русский язык', validators=[MinValueValidator(0), MaxValueValidator(100)])
    math_score = models.IntegerField('Балл Математика', validators=[MinValueValidator(0), MaxValueValidator(100)])
    achievement_score = models.IntegerField('Балл ИД', validators=[MinValueValidator(0), MaxValueValidator(10)])
    total_score = models.IntegerField('Сумма баллов', validators=[MinValueValidator(0), MaxValueValidator(310)])
    has_consent = models.BooleanField('Согласие на зачисление', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Абитуриент'
        verbose_name_plural = 'Абитуриенты'
        indexes = [
            models.Index(fields=['original_id']),
            models.Index(fields=['total_score']),
            models.Index(fields=['has_consent']),
        ]

    def __str__(self):
        return f"Абитуриент #{self.original_id} ({self.total_score} баллов)"

    def save(self, *args, **kwargs):
        # Автоматически пересчитываем сумму баллов при сохранении
        self.total_score = (
                self.physics_score +
                self.russian_score +
                self.math_score +
                self.achievement_score
        )
        super().save(*args, **kwargs)


class Application(models.Model):
    """Заявление абитуриента на конкретную программу"""
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Абитуриент'
    )
    program = models.ForeignKey(
        EducationalProgram,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Образовательная программа'
    )
    priority = models.IntegerField(
        'Приоритет',
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    list_date = models.DateField('Дата конкурсного списка')
    is_active = models.BooleanField('Актуальная запись', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Заявление'
        verbose_name_plural = 'Заявления'
        unique_together = ['applicant', 'program', 'list_date']
        indexes = [
            models.Index(fields=['list_date']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_active']),
            models.Index(fields=['applicant', 'program', 'list_date']),
        ]
        ordering = ['list_date', 'program', '-priority']

    def __str__(self):
        return f"{self.applicant} -> {self.program} (приоритет {self.priority}, {self.list_date})"


class AdmissionResult(models.Model):
    """Результат зачисления на определенную дату"""
    program = models.ForeignKey(
        EducationalProgram,
        on_delete=models.CASCADE,
        related_name='admission_results',
        verbose_name='Образовательная программа'
    )
    calculation_date = models.DateField('Дата расчета')
    passing_score = models.IntegerField('Проходной балл', null=True, blank=True)
    enrolled_count = models.IntegerField('Количество зачисленных', default=0)
    is_shortage = models.BooleanField('Недообор', default=False)
    calculation_time = models.DateTimeField('Время расчета', auto_now_add=True)

    class Meta:
        verbose_name = 'Результат зачисления'
        verbose_name_plural = 'Результаты зачисления'
        unique_together = ['program', 'calculation_date']
        ordering = ['-calculation_date', 'program']

    def __str__(self):
        if self.is_shortage:
            return f"{self.program} ({self.calculation_date}): НЕДОБОР"
        return f"{self.program} ({self.calculation_date}): {self.passing_score} баллов"


class EnrolledApplicant(models.Model):
    """Зачисленный абитуриент"""
    admission_result = models.ForeignKey(
        AdmissionResult,
        on_delete=models.CASCADE,
        related_name='enrolled_applicants',
        verbose_name='Результат зачисления'
    )
    applicant = models.ForeignKey(
        Applicant,
        on_delete=models.CASCADE,
        related_name='enrollment_history',
        verbose_name='Абитуриент'
    )
    priority = models.IntegerField('Приоритет зачисления')
    total_score = models.IntegerField('Сумма баллов')
    enrollment_order = models.IntegerField('Порядковый номер зачисления')

    class Meta:
        verbose_name = 'Зачисленный абитуриент'
        verbose_name_plural = 'Зачисленные абитуриенты'
        ordering = ['enrollment_order']

    def __str__(self):
        return f"{self.applicant} зачислен на {self.admission_result.program}"


class UploadHistory(models.Model):
    """История загрузки файлов"""
    UPLOAD_STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('partial', 'Частично'),
        ('failed', 'Ошибка'),
    ]

    filename = models.CharField('Имя файла', max_length=255)
    program = models.ForeignKey(
        EducationalProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Образовательная программа'
    )
    list_date = models.DateField('Дата списка')
    records_total = models.IntegerField('Всего записей в файле', default=0)
    records_processed = models.IntegerField('Обработано записей', default=0)
    records_created = models.IntegerField('Создано записей', default=0)
    records_updated = models.IntegerField('Обновлено записей', default=0)
    records_deleted = models.IntegerField('Удалено записей', default=0)
    status = models.CharField('Статус', max_length=10, choices=UPLOAD_STATUS_CHOICES)
    error_message = models.TextField('Сообщение об ошибке', blank=True)
    processing_time = models.FloatField('Время обработки (сек)', default=0.0)
    uploaded_at = models.DateTimeField('Время загрузки', auto_now_add=True)

    class Meta:
        verbose_name = 'История загрузки'
        verbose_name_plural = 'История загрузок'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} ({self.list_date}) - {self.get_status_display()}"
