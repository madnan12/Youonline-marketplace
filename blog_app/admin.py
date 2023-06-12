from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(BlogCategory)
admin.site.register(Blog)
admin.site.register(BlogTag)
admin.site.register(BlogWatched)
admin.site.register(BlogMedia)
admin.site.register(BlogAuthor)

