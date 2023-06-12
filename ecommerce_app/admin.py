from django.contrib import admin
from . models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'cost_price', 'sale_price', 'quantity', 'availability', 'is_deleted')
    

class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'image', 'video', 'is_deleted')

class ProductScheduleAdmin(admin.ModelAdmin):
    list_display = ('product', 'profile', 'publish_time', 'is_posted')
    
    
# Register your models here.
admin.site.register(BusinessOwner)
admin.site.register(BusinessDetails)
admin.site.register(ProductCategory)
admin.site.register(ProductSubCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductMedia, ProductMediaAdmin)
admin.site.register(ProductSchedule)
admin.site.register(ArchivedProduct)
admin.site.register(CollectionProduct)