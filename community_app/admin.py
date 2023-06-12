from django.contrib import admin
from . models import *

# Register your models here.
# Group Models
class GroupRequestAdmin(admin.ModelAdmin):
    list_display = ('profile', 'profile_id', 'group', 'status', 'is_active')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_by', 'category_id', 'created_at')


class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'group', 'is_admin')


admin.site.register(GroupCategory)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
admin.site.register(GroupRequest, GroupRequestAdmin)
admin.site.register(GroupRule)
admin.site.register(GroupInvite)

# Page Models

class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_by', 'name', 'is_promoted', 'is_deleted')

class PageBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id', 'banner', 'created_at')

class PageFollowerAdmin(admin.ModelAdmin):
    list_display = ('profile', 'page', 'page_id')

admin.site.register(Page, PageAdmin)
admin.site.register(PageFollower, PageFollowerAdmin)
admin.site.register(PageRule)
admin.site.register(PageBanner, PageBannerAdmin)
admin.site.register(PageCurrentBanner)
admin.site.register(GroupBanner)

admin.site.register(GroupLogo)
admin.site.register(GroupCurrentLogo)
admin.site.register(PageLogo)
admin.site.register(PageCurrentLogo)

