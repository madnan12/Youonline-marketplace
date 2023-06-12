from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.site_header = "YouOnline Administration"
admin.site.site_title = "YouOnline Admin"
admin.site.index_title = "Welcome to YouOnline Administration Portal"

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_admin', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile' ,'video_module', 'media_post', 'video_post', 'created_at', 'poll_post',
                    'cover_post', 'normal_post', 'shared_post')


class ProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile' ,'album', 'picture', 'post', 'created_at', 'is_deleted')


class UserProfilePictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile' ,'picture', 'created_at', 'is_deleted')


class PostMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_id', 'created_at')


class ProfileStoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at', 'is_deleted')


class UserAlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at', 'is_deleted')


class UserAlbumMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'is_deleted', 'image', 'video')


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'gender', 'birth_date', 'is_deleted', 'is_blocked')
    
    def username(self, obj):
        return obj.user.username


class NotifiersListAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_post', 'comment', 'comment_reply')
    
    def get_post(self, obj):
        try:
            return obj.post.id
        except:
            return None

    def comment(self, obj):
        try:
            return obj.post_comment.id
        except:
            return None
    
    def comment_reply(self, obj):
        try:
            return obj.comment_reply.id
        except:
            return None


# User Models
admin.site.register(User, AccountAdmin)
admin.site.register(UserAlbum, UserAlbumAdmin)
admin.site.register(UserAlbumMedia, UserAlbumMediaAdmin)
admin.site.register(AlbumPost)
admin.site.register(UserFamilyRelation)
admin.site.register(UserFamilyMember)
admin.site.register(UserLifeEventCategory)
admin.site.register(UserLifeEvent)
admin.site.register(ProfileCoverAlbum)
admin.site.register(CoverPicture)
admin.site.register(UserCoverPicture)
admin.site.register(ProfilePictureAlbum)
admin.site.register(ProfilePicture, ProfilePictureAdmin)
admin.site.register(UserProfilePicture, UserProfilePictureAdmin)
admin.site.register(UserWorkPlace)
admin.site.register(UserPlacesLived)
admin.site.register(UserAboutYou)
admin.site.register(UserUniversity)
admin.site.register(Relationship)
admin.site.register(RelationshipStatus)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileView)
admin.site.register(LoginHistory)
admin.site.register(UserHighSchool)
admin.site.register(UserPrivacySettings)
admin.site.register(ProfileStory, ProfileStoryAdmin)
admin.site.register(StoryView)
admin.site.register(IgnoredList)



@admin.register(VerificationCode)
class VerficationCodeAdmin(admin.ModelAdmin):
    search_fields = ('code', 'id', 'created_at', 'used', 'expired' , 'user__username')

    list_display = ['id' , 'code' , 'used' , 'expired' , 'get_username', 'created_at']


@admin.register(TagUser)
class TagUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'tagged_profile', 'post', 'tagged_by', 'is_comment', 'is_post', 'is_comment_reply', 'is_mentioned')


# Post Models
admin.site.register(Post, PostAdmin)
admin.site.register(SharedPost)
admin.site.register(SavedPost)
admin.site.register(HiddenPost)
admin.site.register(PostMedia, PostMediaAdmin)
admin.site.register(MediaPostObject)
admin.site.register(PostReaction)
admin.site.register(PostDislike)
admin.site.register(PostComment)
admin.site.register(CommentMedia)
admin.site.register(CommentReaction)
admin.site.register(CommentReply)
admin.site.register(CommentReplyMedia)
admin.site.register(CommentReplyReaction)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country_code', 'dial_code')


class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'country_id')


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'country')


class PollOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'option')


class PollVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'poll', 'profile', 'option')


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['id' , 'name', 'currency_symbol']

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'created_at')

admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Language)
admin.site.register(Industry)
admin.site.register(Company)
admin.site.register(FriendRequest)
admin.site.register(FriendsList)
admin.site.register(Poll)
admin.site.register(PollOption, PollOptionAdmin)
admin.site.register(PollVote, PollVoteAdmin)

# Notifications
admin.site.register(NotifiersList, NotifiersListAdmin)
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['type' , 'text' , 'created_at', 'notifiers_count']

@admin.register(ExceptionRecord)
class ExceptionRecordAdmin(admin.ModelAdmin):
    list_display = ['id' , 'is_resolved' , 'created_at']

admin.site.register(ReportProfileCategory)
admin.site.register(ReportPostCategory)
admin.site.register(ReportPost)
admin.site.register(YouonlineLogo)
admin.site.register(ReportProfile)
admin.site.register(BlockProfile)
admin.site.register(CompanyMedia)
admin.site.register(PackagePlan)
admin.site.register(PackagePlaneDetail)
admin.site.register(ModuleViewHistory)
admin.site.register(DealData)
