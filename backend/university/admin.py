from django.contrib import admin
from .models import (
    EducationalProgram, Applicant, Application,
    AdmissionResult, EnrolledApplicant, UploadHistory
)


@admin.register(EducationalProgram)
class EducationalProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'slug', 'capacity')
    list_filter = ('capacity',)
    search_fields = ('name', 'code')
    ordering = ('name',)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('original_id', 'total_score', 'has_consent', 'created_at')
    list_filter = ('has_consent', 'created_at')
    search_fields = ('original_id', 'full_name')
    readonly_fields = ('total_score', 'created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('original_id', 'full_name', 'has_consent')
        }),
        ('Баллы', {
            'fields': ('physics_score', 'russian_score', 'math_score', 'achievement_score', 'total_score')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 1
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'program', 'priority', 'list_date', 'is_active')
    list_filter = ('program', 'priority', 'list_date', 'is_active')
    search_fields = ('applicant__original_id', 'program__name')
    date_hierarchy = 'list_date'
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


class EnrolledApplicantInline(admin.TabularInline):
    model = EnrolledApplicant
    extra = 0
    readonly_fields = ('enrollment_order',)


@admin.register(AdmissionResult)
class AdmissionResultAdmin(admin.ModelAdmin):
    list_display = ('program', 'calculation_date', 'passing_score', 'enrolled_count', 'is_shortage')
    list_filter = ('program', 'calculation_date', 'is_shortage')
    search_fields = ('program__name',)
    date_hierarchy = 'calculation_date'
    readonly_fields = ('calculation_time',)
    inlines = [EnrolledApplicantInline]

    def has_add_permission(self, request):
        # Запрещаем ручное добавление результатов зачисления
        return False

    def has_change_permission(self, request, obj=None):
        # Запрещаем редактирование результатов зачисления
        return False


@admin.register(UploadHistory)
class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = ('filename', 'program', 'list_date', 'status', 'records_processed', 'processing_time', 'uploaded_at')
    list_filter = ('status', 'program', 'list_date')
    search_fields = ('filename', 'error_message')
    readonly_fields = ('uploaded_at', 'processing_time', 'records_total', 'records_processed',
                       'records_created', 'records_updated', 'records_deleted')
    date_hierarchy = 'uploaded_at'

    def has_add_permission(self, request):
        # Запрещаем ручное добавление записей истории
        return False

    def has_change_permission(self, request, obj=None):
        # Запрещаем редактирование истории
        return False
