from django.contrib import admin
from . models import *

# Register your models here.
class PropertySubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_category', 'category')

    def category(self, obj):
        return obj.sub_category.category


class PropertySubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category')

admin.site.register(Category)
admin.site.register(SubCategory, PropertySubCategoryAdmin)
admin.site.register(SubSubCategory, PropertySubSubCategoryAdmin)


class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'area', 'category', 'profile',
                    'street_adress', 'category', 'sub_category', 'sub_sub_category',
                    'bedrooms', 'baths', 'country', 'state', 'city')


class ClassifiedAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'profile',
                    'category', 'sub_category', 'sub_sub_category',
                    'country', 'state', 'city')


admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyMedia)
admin.site.register(FavouriteProperty)
admin.site.register(PropertySearchHistory)
admin.site.register(ReportProperty)
