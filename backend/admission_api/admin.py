from django.contrib import admin
from .models import Applicant, EducationalProgram, AdmissionData

@admin.register(EducationalProgram)
class EducationalProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'seats')
    list_filter = ('code',)
    search_fields = ('code', 'name')

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_score', 'physics_ikt', 'russian_lang', 'math', 'achievements')
    list_filter = ('total_score',)
    search_fields = ('id',)

@admin.register(AdmissionData)
class AdmissionDataAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'educational_program', 'date', 'has_consent', 'priority')
    list_filter = ('educational_program', 'date', 'has_consent', 'priority')
    search_fields = ('applicant__id',)
    date_hierarchy = 'date'
