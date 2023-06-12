from django.urls import path
from .views import user, post, utility_views, search
from django.conf import settings
from django.conf.urls.static import static
from .views.user import UserAPIView

urlpatterns = [
    # Utility EndPoints
    path('get_countries/', utility_views.get_countries),
    path('get_states/', utility_views.get_states),
    path('get_cities/', utility_views.get_cities),
    path('get_languages/', utility_views.get_languages),
    path('get_currencies/', utility_views.get_currencies),
    path('get_meta/', utility_views.get_meta),
    path('send_error_mail/' , utility_views.send_error_mail),
    path('get_all_error_exceptions/' , utility_views.get_all_error_exceptions),


    path('user/', UserAPIView.as_view(), name='user'),
    # UserRelationShip URLs
    path('delete_relationship/', user.delete_relationship),
    path('add_relationship/', user.add_relationship),
    path('update_relationship/', user.update_relationship),
    path('get_relationship/', user.get_relationship),
    path('get_all_relationships/', user.get_all_relationships),

    # UserProfile Urls
    path('register/', user.register),
    path('verify_email/', user.verify_email),
    path('verify_phone/', user.verify_phone),
    path('resend_code/', user.resend_code),
    path('get_user_profile/', user.get_user_profile),
    path('get_profile_id/', user.get_profile_id),
    path('get_newsfeed/', user.get_newsfeed),
    path('get_timeline/', user.get_timeline),
    path('login/', user.login),
    path('logout_user/', user.logout_user),
    path('forgot_password/', user.forgot_password),
    path('reset_password/', user.reset_password),
    path('change_password/', user.change_password),
    path('add_bio/', user.add_bio),
    path('update_user_profile/', user.update_user_profile),
    path('add_user_activity/', user.add_user_activity),
    path('get_user_activity/', user.get_user_activity),
    path('delete_user_activity/', user.delete_user_activity),
    path('update_user_activity/', user.update_user_activity),
    path('update_contact_info/', user.update_contact_info),
    path('get_bithday_profiles/', user.get_bithday_profiles),
    path('get_my_friend_requests/', user.get_my_friend_requests),
    path('get_report_profile_category/', user.get_report_profile_category),
    path('report_profile/', user.report_profile),
    path('block_profile/', user.block_profile),
    path('progress_profile/', user.progress_profile),
    path('change_privacy/', user.change_privacy),
    path('create_business_profile/', user.create_business_profile),
    path('delete_account/', user.delete_account),
    path('get_business_profile/', user.get_business_profile),
    path('edit_business_profile/', user.edit_business_profile),


    # Social Login URLs
    path('create_social_login/', user.create_social_login),

    # Search URLs
    path('search/', search.search),
    path('search_all/', search.search_all),
    path('search_module/', search.search_module),
    path('search_friends/', search.search_friends),
    path('discover_people/', search.discover_people),
    path('discover_communinty/', search.discover_communinty),
    path('search_my_module_ads/', search.search_my_module_ads),
    path('view_ads_by_profile/', search.view_ads_by_profile),
    path('suggested_ads/', search.suggested_ads),

    # path('get_popular_categories/', search.get_popular_categories),
    # Profile Story
    path('create_profile_story/', user.create_profile_story),
    path('create_story_view/', user.create_story_view),
    path('get_profile_story/', user.get_profile_story),
    path('delete_profile_story/', user.delete_profile_story),
    path('get_all_profile_stories/', user.get_all_profile_stories),
    path('get_all_stories/', user.get_all_stories),

    # UserSettings URLs
    path('update_user_email/', user.update_user_email),
    path('update_user_privacy_settings/', user.update_user_privacy_settings),
    path('get_user_privacy_settings/', user.get_user_privacy_settings),

    # Timeline URLs
    path('get_uploaded_pictures/', user.get_uploaded_pictures),
    path('get_photos_of_you/', user.get_photos_of_you),
    path('get_prev_profile_pictures/', user.get_prev_profile_pictures),
    path('get_prev_cover_pictures/', user.get_prev_cover_pictures),

    # Profile Picture Urls
    path('delete_profile_picture/', user.delete_profile_picture),
    path('add_profile_picture/', user.add_profile_picture),
    
    # Cover Picture Urls
    path('delete_cover_picture/', user.delete_cover_picture),
    path('add_cover_picture/', user.add_cover_picture),
    
    # UserHighSchool Urls
    path('add_user_school/', user.add_user_school),
    path('update_user_school/', user.update_user_school),
    path('get_user_schools/', user.get_user_schools),
    path('get_user_single_school/', user.get_user_single_school),
    path('delete_user_school/', user.delete_user_school),

    # UserPlacedLived Urls
    path('delete_place_lived/', user.delete_place_lived),
    path('add_place_lived/', user.add_place_lived),
    path('update_place_lived/', user.update_place_lived),
    path('get_place_lived/', user.get_place_lived),

    # UserWorkPlace Urls
    path('add_user_workplace/', user.add_user_workplace),
    path('update_user_workplace/', user.update_user_workplace),
    path('delete_user_workplace/', user.delete_user_workplace),
    path('get_user_current_workplace/', user.get_user_current_workplace),
    path('get_user_workplace/', user.get_user_workplace),

    # UserFamilyMember Urls
    path('add_family_member/', user.add_family_member),
    path('approve_family_member/', user.approve_family_member),
    path('delete_family_member/', user.delete_family_member),
    path('get_all_family_members/', user.get_all_family_members),
    

    # UserAlbum Urls
    path('delete_user_album/', user.delete_user_album),
    path('add_user_album/', user.add_user_album),
    path('update_user_album/', user.update_user_album),
    path('get_user_album/', user.get_user_album),
    path('get_all_user_albums/', user.get_all_user_albums),

    # UserAlbumMedia Urls
    path('add_user_album_media/', user.add_user_album_media),
    path('get_user_album_media/', user.get_user_album_media),
    path('delete_user_album_media/', user.delete_user_album_media),

    # Notifications Urls
    path('get_notifications/', user.get_notifications),
    path('remove_notification/', user.remove_notification),
    path('turn_of_notification/' , user.turn_of_notification),
    path('save_fcmdevice/', user.save_fcmdevice),
    path('get_business_profile_stats/', user.get_business_profile_stats),

    path('post_notification_choice/', post.post_notification_choice),

    # Post Module
    path('create_post/', post.create_post),
    path('get_single_deal/', post.get_single_deal),
    
    path('get_post/', post.get_post),
    path('update_post/', post.update_post),
    path('add_single_post_media/', post.add_single_post_media),
    path('delete_post_media/', post.delete_post_media),
    path('delete_post/', post.delete_post),
    path('hide_post/', post.hide_post),
    path('unhide_post/', post.unhide_post),
    path('get_all_hidden_posts/', post.get_all_hidden_posts),
    path('vote_poll/', post.vote_poll),
    path('undo_vote/', post.undo_vote),
    path('create_posts_reactions/', post.create_posts_reactions),
    path('total_posts_reactions/', post.total_posts_reactions),
    path('get_report_post_category/', post.get_report_post_category),
    path('report_post/', post.report_post),

    # Save Post Urls
    path('save_post/', post.save_post),
    path('un_save_post/', post.un_save_post),
    path('get_all_saved_posts/', post.get_all_saved_posts),
    path('get_saved_video_module_posts/', post.get_saved_video_module_posts),

    path('add_post_comment/', post.add_post_comment),
    path('create_post_reaction/', post.create_post_reaction),
    path('single_post_reactions/', post.single_post_reactions),
    path('create_post_comment_reaction/', post.create_post_comment_reaction),

    path('add_post_comment/', post.add_post_comment),
    path('add_comment_reply/', post.add_comment_reply),
    path('delete_post_comment/', post.delete_post_comment),
    path('create_post_reaction/', post.create_post_reaction),
    path('create_post_comment_reaction/', post.create_post_comment_reaction),
    path('create_comment_reply_reaction/', post.create_comment_reply_reaction),
    path('get_post_comments/', post.get_post_comments),
    path('delete_comment_reply/', post.delete_comment_reply),
    path('dislike_post/', post.dislike_post),
    path('popular_category/', post.popular_category),

    # Share Post
    path('share_post/', post.share_post),
    path('share_post_to_friend_timeline/', post.share_post_to_friend_timeline),

    # Friends module Urls
    path('create_friend_request/', user.create_friend_request),
    path('confirm_friend_request/', user.confirm_friend_request),
    path('remove_friend/', user.remove_friend),
    path('get_following_list/', user.get_following_list),
    path('get_followers_list/', user.get_followers_list),
    path('get_all_friends/', user.get_all_friends),
    path('get_friend_requests/', user.get_friend_requests),
    path('mark_as_read_friend_requests/' , user.mark_as_read_friend_requests),
    path('follow/', user.follow),
    path('unfollow/', user.unfollow),
    path('suggested_people/', user.suggested_people),
    path('ignore_suggested/', user.ignore_suggested),

    # Package Plan
    path('buy_package/', post.buy_package),
    path('get_packages/', post.get_packages),

    # Deals URL 
    path('create_deal/', post.create_deal),
    path('delete_deal/', post.delete_deal),
    path('update_deal/', post.update_deal),

    # Huzaifa's Testing
    path('d-image/' , user.testImageLabel),
    path('test/' , user.TestingRandom),
    path('send_socket_notification/' , user.send_socket_notification),
    path('test-posts/' , post.get_all_test_posts),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
