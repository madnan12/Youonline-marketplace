from django.contrib import admin
from . models import *

# Register your models here.


class ClassifiedSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'is_business_directory', 'category_id', 'image')

class FavouriteClassifiedAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'classified', 'created_at')

class ClassifiedAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name','created_at', 'business_directory','country', 'state', 'city', 'category', 
        'get_sub_category_name', 'currency', 'price', 
        )

class ClassifiedMakeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'subcategory', 'background_color',
        )
@admin.register(ClassifiedCategory)
class ClassifiedCategoryAdmin(admin.ModelAdmin):
    list_display = ['title' , 'business_directory', 'id' , 'is_deleted', 'image']

admin.site.register(Classified, ClassifiedAdmin)
admin.site.register(ClassifiedMedia)
admin.site.register(ClassifiedSubCategory, ClassifiedSubCategoryAdmin)
admin.site.register(ClassifiedSubSubCategory)
admin.site.register(FavouriteClassified, FavouriteClassifiedAdmin)
admin.site.register(ClassifiedSearchHistory)
admin.site.register(ClassifiedeMake, ClassifiedMakeAdmin)
admin.site.register(ReportClassified)
