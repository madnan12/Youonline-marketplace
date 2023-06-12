from django.urls import path
from . import views as community
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Group URLs
    path('create_group/', community.create_group),
    path('update_group/', community.update_group),
    path('delete_group/', community.delete_group),
    path('add_group_banner/', community.add_group_banner),
    path('add_group_logo/', community.add_group_logo),
    path('delete_group_logo/', community.delete_group_logo),
    path('get_group/', community.get_group),
    path('get_all_group_categories/', community.get_all_group_categories),
    path('get_all_user_groups/', community.get_all_user_groups),

    path('discover_groups/', community.discover_groups),
    path('get_friends_groups/', community.get_friends_groups),
    
    # Group Requests
    path('group_join_request/', community.group_join_request),
    path('confirm_group_join_request/', community.confirm_group_join_request),
    path('make_group_admin/', community.make_group_admin),
    path('remove_member/', community.remove_member),
    path('leave_group/', community.leave_group),
    path('get_all_group_requests/', community.get_all_group_requests),
    path('get_all_group_admins/', community.get_all_group_admins),
    path('get_all_group_members/', community.get_all_group_members),
    path('get_all_group_members_ids/', community.get_all_group_members_ids),

    # Group Rules
    path('create_group_rule/', community.create_group_rule),
    path('update_group_rule/', community.update_group_rule),
    path('delete_group_rule/', community.delete_group_rule),
    path('get_all_group_rules/', community.get_all_group_rules),

    # Group Invites
    path('create_group_invite/', community.create_group_invite),
    path('cancel_group_invite/', community.cancel_group_invite),
    path('get_all_group_invites/', community.get_all_group_invites),
    path('get_all_group_invite_profiles/', community.get_all_group_invite_profiles),
    path('get_user_group_invites/', community.get_user_group_invites),
    path('accept_group_invite/', community.accept_group_invite),

    # Group Posts
    path('get_group_posts/', community.get_group_posts),
    path('user_groups_feed/', community.user_groups_feed),
    path('group_image_posts/', community.group_image_posts),
    path('group_video_posts/', community.group_video_posts),

    # Group Posts Approval
    path('group_pending_posts/', community.group_pending_posts),
    path('approve_pending_group_post/', community.approve_pending_group_post),
    path('approve_all_pending_group_posts/', community.approve_all_pending_group_posts),

    # Page URLs
    path('create_page/', community.create_page),
    path('update_page/', community.update_page),
    path('delete_page/', community.delete_page),
    path('add_page_banner/', community.add_page_banner),
    path('update_page_banner/', community.update_page_banner),
    path('add_page_logo/', community.add_page_logo),
    path('discover_pages/', community.discover_pages),
    path('get_page/', community.get_page),
    path('delete_page_logo/', community.delete_page_logo),
    
    # Page Followers URLs
    path('follow_page/', community.follow_page),
    path('get_followed_pages/', community.get_followed_pages),
    path('make_page_admin/', community.make_page_admin),
    path('unfollow_page/', community.unfollow_page),
    path('get_all_page_members/', community.get_all_page_members),
    path('get_all_page_members_ids/', community.get_all_page_members_ids),
    path('change_page_member_role/' , community.change_page_member_role ),

    # Page Rules
    path('create_page_rule/', community.create_page_rule),
    path('update_page_rule/', community.update_page_rule),
    path('delete_page_rule/', community.delete_page_rule),
    path('get_all_page_rules/', community.get_all_page_rules),

    # Page Posts
    path('get_page_posts/', community.get_page_posts),
    path('user_pages_feed/', community.user_pages_feed),
    path('page_image_posts/', community.page_image_posts),
    path('page_video_posts/', community.page_video_posts),

    # Page Invites
    path('create_page_invite/', community.create_page_invite),
    path('cancel_page_invite/', community.cancel_page_invite),
    path('get_all_page_invites/', community.get_all_page_invites),
    path('get_all_page_invite_profiles/', community.get_all_page_invite_profiles),
    path('get_user_page_invites/', community.get_user_page_invites),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
