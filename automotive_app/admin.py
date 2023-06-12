from django.contrib import admin
from . models import *

# Register your models here.
class AutomotiveMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'automotive_image', 'automotive_video', 'automotive')


class AutomotiveAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','country', 'state', 'city', 'make', 'automotive_model', 'created_at')


class AutomotiveMakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'imgae')


class AutomotiveSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'category_id', 'image')


class AutomotiveMakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'image', 'sub_category')


admin.site.register(AutomotiveMake, AutomotiveMakeAdmin)
admin.site.register(AutomotiveModel)
admin.site.register(Automotive, AutomotiveAdmin)
admin.site.register(FavouriteAutomotive)
admin.site.register(AutomotiveMedia, AutomotiveMediaAdmin)
admin.site.register(AutomotiveCategory)
admin.site.register(AutomotiveSubCategory, AutomotiveSubCategoryAdmin)
admin.site.register(AutomotiveSubSubCategory)
admin.site.register(AutomotiveComparison)
admin.site.register(AutomotiveSearchHistory)
admin.site.register(ReportAutomotive)
