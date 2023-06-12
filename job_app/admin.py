from atexit import register
from django.contrib import admin
from . models import *
from django import forms

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'company', 'profile', 'salary_start_range', 'salary_end_range', 'position_type')


class JobProjectMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'jobprofile', 'jobproject', 'created_at')

class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'title')

admin.site.register(FavoriteJob)
admin.site.register(Skill)
admin.site.register(JobApply)
admin.site.register(JobProfile)
admin.site.register(JobProject)
admin.site.register(JobAlert)
admin.site.register(JobSearchHistory)
admin.site.register(JobStory)
admin.site.register(JobEndoresements)
admin.site.register(JobProjectMedia, JobProjectMediaAdmin)
admin.site.register(JobCategory, JobCategoryAdmin)
admin.site.register(JobMedia)
admin.site.register(CompanyCategory)
admin.site.register(CompanyLogo)
admin.site.register(CompanyCoverImage)
admin.site.register(JobApplyMedia)
admin.site.register(ReportJob)


