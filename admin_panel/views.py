from tokenize import group
from django.shortcuts import render, redirect
from automotive_app.models import Automotive, AutomotiveCategory, AutomotiveMake
from classified_app.models import Classified, ClassifiedCategory
from community_app.models import Group, GroupCategory, Page
from job_app.models import Job, JobApply, JobProfile
from youonline_social_app.models import AlbumPost, PostMedia, Profile, Post, PostComment, ProfilePicture, ProfilePictureAlbum, UserAlbum,  UserPlacesLived, ProfileStory, User, UserProfilePicture
from blog_app.models import Blog, BlogCategory
from video_app.models import Video, VideoCategory, VideoChannel
from chat_app.models import ChatMessage
from property_app.models import  Category, Property
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login as dj_login,logout
from django.db.models import  Q
import datetime
from datetime import date
from django.contrib.auth.decorators import login_required
from youonline_social_app.decorators import superuser_required
from admin_panel.forms import UserForm, ProfileForm, LoginForm
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Create your views here.

# admin dashboard
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_home(request):
    today = datetime.datetime.now()
    current_month = today.month
    current_year = date.today().year
    month_list = ['Jan', 'Feb', 'Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    user_list = []
    active_user_list = []
    post_list = []
    group_list = []
    promote_group_list = []
    group_post_list = []
    page_list = []
    promote_page_list = []
    page_post_list = []
    property_list = []
    promoted_property_list = []
    automotive_list = []
    promote_automotive_list = []
    classified_list = []
    promote_classified_list = []
    channel_list = []
    video_list = []
    job_list = []
    blog_list = []
    jobprofile_list = []
    promoted_blog_list = []
    business_directory_list = []
    promoted_business_diretory = []
    inactive_user_list = []
    chat_list = []

    for m in range(current_month):
        months = m+1
        total_user_graph = Profile.objects.filter(
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_active_user_graph = Profile.objects.filter(
                                        user__is_active=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_inactive_user_graph = Profile.objects.filter(
                                        user__is_active=False,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_post_graph = Post.objects.filter(
                                        group_post=False, 
                                        page_post=False, 
                                        blog_post=False ,
                                        video_module=False,
                                        property_post=False,
                                        automotive_post=False,
                                        classified_post=False,
                                        group_banner=False,
                                        page_banner=False,
                                        story_post=False,
                                        job_post=False,
                                        normal_post=True,
                                        is_deleted=False, 
                                        job_project_post=False,                        
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_group_graph = Group.objects.filter(
                                        is_deleted=False,  
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promote_group_graph = Group.objects.filter(
                                        is_deleted=False, 
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_group_post_graph = Post.objects.filter(
                                        is_deleted=False,
                                        group_post=True,
                                        created_at__month=months, 
                                        created_at__year=current_year).exclude(group=None)
        total_page_graph = Page.objects.filter(
                                        is_deleted=False,  
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promote_page_graph = Page.objects.filter(
                                        is_deleted=False, 
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_page_post_graph = Post.objects.filter(
                                        is_deleted=False, 
                                        page_post=True,
                                        created_at__month=months, 
                                        created_at__year=current_year).exclude(page=None)
        total_property_graph = Property.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False, 
                                        created_at__month=months,
                                        created_at__year=current_year)
        total_promote_property_graph = Property.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False, 
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)

        total_automotive_graph = Automotive.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False, 
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promote_automotive_graph = Automotive.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False,
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_classified_graph = Classified.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False,
                                        business_directory=False, 
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promote_classified_graph = Classified.objects.filter(
                                        verification_status='Verified',
                                        business_directory=False,
                                        is_deleted=False, 
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_channel_graph = VideoChannel.objects.filter(
                                        is_deleted=False, 
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_video_graph = Video.objects.filter(
                                        is_deleted=False, 
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_job_graph = Job.objects.filter(
                                        is_deleted=False,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_jobprofile_graph = JobProfile.objects.filter(
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_blog_graph = Blog.objects.filter(
                                        is_deleted=False,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promoted_blog_graph = Blog.objects.filter(
                                        is_deleted=False,
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_business_directory_graph = Classified.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False,
                                        business_directory=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_promoted_business_directory = Classified.objects.filter(
                                        verification_status='Verified',
                                        is_deleted=False,
                                        business_directory=True,
                                        is_promoted=True,
                                        created_at__month=months, 
                                        created_at__year=current_year)
        total_chat_graph = ChatMessage.objects.filter(
                                    is_deleted=False,
                                    created_at__month=months, 
                                    created_at__year=current_year
                                        )
                 
        user_list.append(total_user_graph)
        active_user_list.append(total_active_user_graph)
        inactive_user_list.append(total_inactive_user_graph)
        post_list.append(total_post_graph)
        group_list.append(total_group_graph)
        promote_group_list.append(total_promote_group_graph)
        page_list.append(total_page_graph)
        page_post_list.append(total_page_post_graph)
        promote_page_list.append(total_promote_page_graph)
        property_list.append(total_property_graph)
        promoted_property_list.append(total_promote_property_graph)
        automotive_list.append(total_automotive_graph)
        promote_automotive_list.append(total_promote_automotive_graph)
        classified_list.append(total_classified_graph)
        promote_classified_list.append(total_promote_classified_graph)
        channel_list.append(total_channel_graph)
        video_list.append(total_video_graph)
        job_list.append(total_job_graph)
        blog_list.append(total_blog_graph)
        jobprofile_list.append(total_jobprofile_graph)
        promoted_blog_list.append(total_promoted_blog_graph)
        business_directory_list.append(total_business_directory_graph)
        promoted_business_diretory.append(total_promoted_business_directory)
        group_post_list.append(total_group_post_graph)
        chat_list.append(total_chat_graph)

    total_profile = Profile.objects.all().count()
    total_group = Group.objects.filter(
                                    is_deleted=False).count()
    total_unpermote_group = Group.objects.filter(
                                    is_deleted=False, 
                                    is_promoted=False).count()
    total_permote_group = Group.objects.filter(
                                    is_deleted=False, 
                                    is_promoted=True).count()
    total_page = Page.objects.filter(
                                    is_deleted=False).count()
    total_unpermote_page = Page.objects.filter(
                                    is_deleted=False, 
                                    is_promoted=False).count()
    total_permote_page = Page.objects.filter(
                                    is_deleted=False, 
                                    is_promoted=True).count()
    total_post = Post.objects.filter(
                                    group_post=False,
                                    page_post=False, 
                                    is_deleted=False,
                                    normal_post=True, 
                                    blog_post=False).count()
    total_property = Property.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False).count()
    total_unpermote_property = Property.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False, 
                                    is_promoted=False).count()
    total_permote_property = Property.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False, 
                                    is_promoted=True).count()
    total_automotive = Automotive.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False).count()
    total_unpermote_automotive = Automotive.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False, 
                                    is_promoted=False).count()
    total_permote_automotive = Automotive.objects.filter(
                                    verification_status='Verified',
                                    is_deleted=False, 
                                    is_promoted=True).count()
    total_classified = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=False,
                                    is_deleted=False).count()
    total_unpermote_classified = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=False,
                                    is_deleted=False, 
                                    is_promoted=False).count()
    total_permote_classified = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=False,
                                    is_deleted=False, 
                                    is_promoted=True).count()
    total_group_post = Post.objects.filter(
                                    group_post=True, 
                                    is_deleted=False).count()
    total_page_post = Post.objects.filter(
                                    page_post=True, 
                                    is_deleted=False).count()
    total_comment = PostComment.objects.filter(
                                    is_deleted=False).count()
    total_chat = ChatMessage.objects.filter(
                                    is_deleted=False).count()
    total_profile_story = ProfileStory.objects.filter(
                                    is_deleted=False).count()
    total_active_user = Profile.objects.filter(
                                    is_deleted=False,
                                    user__is_active=True).count()
    total_inactive_user = Profile.objects.filter(
                                    user__is_active=False).count()
    pending_property = Property.objects.filter(
                                    verification_status='Pending',
                                    is_deleted=False).count()
    pending_automotive = Automotive.objects.filter(
                                    verification_status='Pending',
                                    is_deleted=False).count()
    pending_classified = Classified.objects.filter(
                                    verification_status='Pending',
                                    business_directory=False,
                                    is_deleted=False).count()
    total_video = Video.objects.filter(
                                    is_deleted=False).count()
    total_video_channel = VideoChannel.objects.filter(
                                    is_deleted=False).count()
    total_job = Job.objects.filter(
                                    is_deleted=False).count()
    total_blog = Blog.objects.filter(
                                    is_deleted=False).count()
    total_business_directory = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=True,
                                    is_deleted=False).count()
    pending_business_directory = Classified.objects.filter(
                                    verification_status='Pending',
                                    business_directory=True,
                                    is_deleted=False,
                                    ).count()
    total_promote_business_directory = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=True,
                                    is_deleted=False,
                                    is_promoted=True
                                    ).count()
    total_unpromote_business_directory = Classified.objects.filter(
                                    verification_status='Verified',
                                    business_directory=True,
                                    is_deleted=False,
                                    is_promoted=False
                                    ).count()
    total_album = UserAlbum.objects.filter(is_deleted=False).count()
    total_job_profile = JobProfile.objects.filter(is_deleted=False).count()
    total_promoted_blogs = Blog.objects.filter(is_deleted=False, is_promoted=True).count()
    total_unpromoted_blogs = Blog.objects.filter(is_deleted=False, is_promoted=False).count()

    context = {
        'total_profile': total_profile,
        'total_group': total_group,
        'total_unpermote_group':total_unpermote_group,
        'total_permote_group':total_permote_group,
        'total_page':total_page,
        'total_unpermote_page':total_unpermote_page,
        'total_permote_page':total_permote_page,
        'total_post':total_post,
        'total_property':total_property,
        'total_unpermote_property':total_unpermote_property,
        'total_permote_property':total_permote_property,
        'total_automotive':total_automotive,
        'total_unpermote_automotive':total_unpermote_automotive,
        'total_permote_automotive':total_permote_automotive,
        'total_group_post':total_group_post,
        'total_page_post':total_page_post,
        'total_comment':total_comment,
        'total_chat':total_chat,
        'total_profile_story':total_profile_story,
        'total_active_user':total_active_user,
        'total_inactive_user':total_inactive_user,
        'pending_property':pending_property,
        'pending_automotive':pending_automotive,
        'total_classified':total_classified,
        'total_unpermote_classified':total_unpermote_classified,
        'total_permote_classified':total_permote_classified,
        'pending_classified':pending_classified,
        'total_video':total_video,
        'total_video_channel':total_video_channel,
        'total_job':total_job,
        'job_list':job_list,
        'jobprofile_list':jobprofile_list,
        'total_blog':total_blog,
        'total_promoted_blogs':total_promoted_blogs,
        'total_unpromoted_blogs':total_unpromoted_blogs,
        'blog_list':blog_list,
        'promoted_blog_list':promoted_blog_list,
        'user_list':user_list,
        'active_user_list':active_user_list,
        'inactive_user_list':inactive_user_list,
        'post_list':post_list,
        'month_list':month_list,
        'group_list':group_list,
        'promote_group_list':promote_group_list,
        'group_post_list':group_post_list,
        'page_list':page_list,
        'promote_page_list':promote_page_list,
        'page_post_list':page_post_list,
        'property_list':property_list,
        'promoted_property_list':promoted_property_list,
        'automotive_list':automotive_list,
        'promote_automotive_list':promote_automotive_list,
        'classified_list':classified_list,
        'promote_classified_list':promote_classified_list,
        'channel_list':channel_list,
        'video_list':video_list,
        'total_business_directory':total_business_directory,
        'pending_business_directory':pending_business_directory,
        'total_promote_business_directory':total_promote_business_directory,
        'total_unpromote_business_directory':total_unpromote_business_directory,
        'business_directory_list':business_directory_list,
        'promoted_business_diretory':promoted_business_diretory,
        'total_album':total_album,
        'total_job_profile':total_job_profile,
        'chat_list':chat_list,
    }
    return render(request, 'adminpanel/index.html', context)

# admin login
def admin_panel_login(request):
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            if user.is_active and user.is_admin:
                dj_login(request, user)
                return HttpResponseRedirect('/admin_panel')
            else:
                form = LoginForm(request.POST or None)
    context={
        'form':form,
    }
    return render(request, 'adminpanel/login.html', context)

# admin panle profile
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_profile(request):
    profile = Profile.objects.get(user=request.user, user__is_active=True)
    context = {
        'profile':profile,
    }
    return render(request, 'adminpanel/profile.html', context)

# admin panel update profile
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_update_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user, user__is_active=True, is_deleted=False)
    form1 = UserForm(instance=user)
    form2 = ProfileForm(instance=profile)
    if request.method == 'POST':
        form1 = UserForm(request.POST or None, instance=user)
        form2 = ProfileForm(request.POST or None, instance=profile)
        if form1.is_valid() and form2.is_valid():
            f1=form1.save()
            f1.save()
            f2=form2.save(commit=False)
            f2.user=f1
            user2=f2.save()
            return redirect('/admin_panel/admin_panel_profile')
        else:
            form1 = UserForm(instance=user)
            form2 = ProfileForm(instance=profile)
    context = {
        'form1':form1,
        'form2':form2,
    }
    return render(request, 'adminpanel/edit_profile.html', context)

# admin panel update profile picture
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_update_profile_picture(request):
    profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
    profile_picture_album = ProfilePictureAlbum.objects.get(profile=profile, is_deleted=False)
    if request.method == 'POST':
        picture = request.FILES.get('picture')
        post = Post.objects.create(profile=profile, profile_picture_post=True ,normal_post=True)
        profile_picture = ProfilePicture.objects.create(profile=profile, post=post, album=profile_picture_album, picture=picture)
        try:
            picture_obj = UserProfilePicture.objects.get(profile=profile)
        except ObjectDoesNotExist:
            picture_obj = UserProfilePicture.objects.create(profile=profile)
        picture_obj.picture = profile_picture
        picture_obj.save()
        return redirect('/admin_panel/admin_panel_profile')
    return render(request, 'adminpanel/profile.html')

# admin logout
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_logout(request):
    logout(request)
    return redirect('/admin_panel/admin_panel_login')

# admin view all Profiles
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_users(request):   
    all_profiles = Profile.objects.all().order_by('-created_at')
    paginator = Paginator(all_profiles, 50)
    page_number = request.GET.get('page')
    profiles = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'profiles': profiles,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_user.html', context)

# admin search user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_user(request):
    get_first_name = request.GET.get('first_name')
    get_last_name= request.GET.get('last_name')
    get_username = request.GET.get('username')
    get_email = request.GET.get('email')
    gender = request.GET.get('gender')
    front_end_server = settings.FRONTEND_SERVER_NAME
    all_profiles = None

    if get_first_name:
        first_name = get_first_name.strip()
    else:
        first_name = ''
    if get_last_name:
        last_name = get_last_name.strip()
    else:
        last_name = ''
    if get_username:
        username = get_username.strip()
    else:
        username = ''
    if get_email:
        email = get_email.strip()
    else:
        email = ''
    
    if gender and not email:
        all_profiles = Profile.objects.filter(
                                Q(gender=gender)&
                                Q(user__first_name__icontains = first_name)&
                                Q(user__last_name__icontains = last_name)&
                                Q(user__username__icontains = username),
                                )
    elif email and not gender:
        all_profiles = Profile.objects.filter(
                                Q(user__first_name__icontains = first_name)&
                                Q(user__last_name__icontains = last_name)&
                                Q(user__username__icontains = username)&
                                Q(user__email__iexact = email),
                                )
    elif gender or email:
        all_profiles = Profile.objects.filter(
                                Q(gender=gender)&
                                Q(user__first_name__icontains = first_name)&
                                Q(user__last_name__icontains = last_name)&
                                Q(user__username__icontains = username)&
                                Q(user__email__iexact = email),
                                )
    else:
        all_profiles = Profile.objects.filter(
                                Q(user__first_name__icontains = first_name)&
                                Q(user__last_name__icontains = last_name)&
                                Q(user__username__icontains = username),
                                )
    paginator = Paginator(all_profiles, 20)
    page_number = request.GET.get('page')
    profiles = paginator.get_page(page_number)
    context = {
        'profiles': profiles,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_user.html', context)

# admin delete user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_user(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        profile1 = Profile.objects.get(pk=id)
        user = profile1.user        
        current_time = datetime.datetime.now()
        end_date = current_time + relativedelta(months=+2) + timedelta()
        profile1.remove_at = end_date
        profile1.is_deleted = True
        user.is_active = False
        user.save()
        profile1.save()

        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin block user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_block_user(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        profile1 = Profile.objects.get(pk=id)
        user = profile1.user
        if not profile1.remove_at and profile1.is_deleted:
            user.is_active = True
            user.save()
            profile1.is_deleted = False
            profile1.is_blocked = False
            profile1.save()
        elif not profile1.remove_at:
            user.is_active = False
            user.save()
            profile1.is_deleted = True
            profile1.is_blocked =True
            profile1.save()
        else:
            pass
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view story
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_profile_story(request):
    all_profile_stories=ProfileStory.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_profile_stories, 50)
    page_number = request.GET.get('page')
    profile_stories = paginator.get_page(page_number)
    context={
        'profile_stories':profile_stories,
    }
    return render(request, 'adminpanel/total_story.html', context)

# admin view single profiile story
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_single_profile_story(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        profile_story = ProfileStory.objects.get(pk=id, is_deleted=False)
        media_story=profile_story.media.url
        if profile_story.text:
            profile_story_data={"text":profile_story.text}
        elif media_story:
            profile_story_data={"media":media_story}
        elif profile_story.text==True and media_story==True:
            profile_story_data={"text":profile_story.text, "media":media_story}
        return JsonResponse(profile_story_data)

# admin delete profiile story
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_profile_story(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        profile_story1 = ProfileStory.objects.get(pk=id, is_deleted=False)
        profile_story1.is_deleted = True
        profile_story1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin search profile story
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_profile_story(request):
    get_username = request.GET.get('username')
    date = request.GET.get('date')
    username = get_username.strip()
    profile_stories = []    
    if date:
        year, month, day = date.split('-')
        my_date=datetime.date(int(year), int(month), int(day))
    if not username and not date:
        messages.error(request, 'Please enter username or date!')
    elif date:
        all_profile_stories = ProfileStory.objects.filter(
                                        Q(created_at__date = my_date), 
                                        is_deleted=False)
        paginator = Paginator(all_profile_stories, 20)
        page_number = request.GET.get('page')
        profile_stories = paginator.get_page(page_number)
    elif username:
        all_profile_stories = ProfileStory.objects.filter(
                                Q(profile__user__username__icontains = username),
                                is_deleted=False)
                                                                                 
        paginator = Paginator(all_profile_stories, 20)
        page_number = request.GET.get('page')
        profile_stories = paginator.get_page(page_number)
    elif username and date:
        all_profile_stories = ProfileStory.objects.filter(
                                Q(profile__user__username__icontains = username)&
                                Q(created_at__date = my_date), 
                                                is_deleted=False)
        paginator = Paginator(all_profile_stories, 20)
        page_number = request.GET.get('page')
        profile_stories = paginator.get_page(page_number)
    context = {
        'profile_stories': profile_stories,
    }
    return render(request, 'adminpanel/search_story.html', context)

# admin view active user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_active_user(request):
    all_profiles = Profile.objects.filter(is_deleted=False, user__is_active=True).order_by('-created_at')
    paginator = Paginator(all_profiles, 50)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'users':users,
    }
    return render(request, 'adminpanel/total_active_user.html', context)

# admin search  active user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_active_user(request):
    get_first_name = request.GET.get('first_name')
    get_last_name = request.GET.get('last_name')
    get_username = request.GET.get('username')
    gender = request.GET.get('gender')
    first_name = get_first_name.strip()
    last_name = get_last_name.strip()
    username = get_username.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not first_name:
        first_name = ''
    if not last_name:
        last_name = ''
    if not username:
        username = ''
    if not gender:
        gender = ''
    if gender:
        all_profiles = Profile.objects.filter(
                            Q(gender = gender), 
                            is_deleted = False, 
                            user__is_active = True)
        paginator = Paginator(all_profiles, 20)
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)
    else:
        all_profiles=Profile.objects.filter(
                            Q(user__first_name__icontains = first_name) &
                            Q(user__last_name__icontains = last_name)&
                            Q(user__username__icontains = username), is_deleted = False, user__is_active=True)
        paginator = Paginator(all_profiles, 20)
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)
    context = {
        'users': users,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_active_user.html', context)

# admin delete active user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_active_user(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        profile1 = Profile.objects.get(pk=id, is_deleted=False)
        user = profile1.user
        user.is_active = False
        user.save()
        profile1.is_deleted = True
        profile1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view inactive user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_inactive_user(request):
    all_users = User.objects.filter(is_active=False)
    paginator = Paginator(all_users, 50)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    context={
        'users':users,
    }
    return render(request, 'adminpanel/total_inactive_user.html', context)

# admin search inactive user
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_inactive_user(request):
    get_first_name = request.GET.get('first_name')
    get_last_name = request.GET.get('last_name')
    get_username = request.GET.get('username')
    first_name = get_first_name.strip()
    last_name = get_last_name.strip()
    username = get_username.strip()
    if not first_name:
        first_name = ''
    if not last_name:
        last_name = ''
    if not username:
        username = ''
    all_profiles = User.objects.filter(
                        Q(first_name__icontains=first_name) &
                        Q(last_name__icontains=last_name)&
                        Q(username__icontains=username)
                        , is_active=False)
    paginator = Paginator(all_profiles, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    context = {
        'users': users,
    }
    return render(request, 'adminpanel/search_inactive_user.html', context)

# admin view user posts
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_user_post(request):
    all_user_posts = Post.objects.filter(
                        group_post=False, 
                        page_post=False, 
                        blog_post=False ,
                        video_module=False,
                        property_post=False,
                        automotive_post=False,
                        classified_post=False,
                        group_banner=False,
                        page_banner=False,
                        story_post=False,
                        job_post=False,
                        job_project_post=False,
                        normal_post=True,
                        is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_user_posts, 50)
    page_number = request.GET.get('page')
    user_posts = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'user_posts':user_posts,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_user_post.html', context)

# admin search user post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_user_post(request):
    get_admin = request.GET.get('admin')
    poll=request.GET.get('poll')
    date=request.GET.get('date')
    image=request.GET.get('image')
    video=request.GET.get('video')
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    postmedia = PostMedia.objects.filter(is_deleted=False)
    all_user_posts = ''
    my_date = None
    if date:
        year, month, day = date.split('-')
        my_date = datetime.date(int(year), int(month), int(day))
    if admin and date and poll:
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                profile__user__username__icontains=admin, 
                                created_at__date=my_date, poll_post=True)
    elif admin and not date and poll:
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,             
                                profile__user__username__icontains=admin, 
                                poll_post=True)
    elif not admin and  date and  poll:
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,             
                                created_at__date=my_date, 
                                poll_post=True)
    elif not admin and not date and poll:
        all_user_posts = Post.objects.filter(
                               group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False, 
                                poll_post=True)
    elif admin and date and image:
        medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                profile__user__username__icontains=admin, 
                                created_at__date=my_date, 
                                id__in=medias)
    elif admin and not date and image:
        medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,            
                                profile__user__username__icontains=admin, 
                                id__in=medias)
    elif not admin and  date and  image:
        medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                created_at__date=my_date, 
                                id__in=medias)
    elif not admin and not date and image:
        medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                               group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,
                                id__in=medias)
    elif admin and date and video:
        medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                profile__user__username__icontains=admin, 
                                created_at__date=my_date, 
                                id__in=medias)
    elif admin and not date and video:
        medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                profile__user__username__icontains=admin, 
                                id__in=medias)
    elif not admin and  date and  video:
        medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                created_at__date=my_date, 
                                id__in=medias)
    elif not admin and not date and video:
        medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
        all_user_posts = Post.objects.filter(
                               group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,
                                id__in=medias)
    elif admin and date and not poll and not image and not video:
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,            
                                profile__user__username__icontains=admin, 
                                created_at__date=my_date)
    elif admin and not date and not poll and not image and not video:
        all_user_posts = Post.objects.filter(
                                group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                normal_post=True,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,            
                                profile__user__username__icontains=admin)
    elif not admin and  date and not poll and not image and not video:
        all_user_posts = Post.objects.filter(
                               group_post=False, 
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                normal_post=True,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,     
                                created_at__date=my_date)
    paginator = Paginator(all_user_posts, 20)
    page_number = request.GET.get('page')
    user_posts = paginator.get_page(page_number)
    context = {
        'user_posts': user_posts,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_user_post.html', context)

# admin delete user post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_user_post(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        user_post1 = Post.objects.get(
                            pk=id, 
                            group_post=False, 
                            page_post=False,
                            is_deleted=False)
        user_post1.is_deleted = True
        user_post1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view single user posts
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_single_user_all_post(request, id):
    profile = Profile.objects.get(id=id)
    postmedia = PostMedia.objects.filter(is_deleted=False)
    front_end_server = settings.FRONTEND_SERVER_NAME
    poll=request.GET.get('poll')
    date=request.GET.get('date')
    image=request.GET.get('image')
    video=request.GET.get('video')
    album = request.GET.get('album')
    profile_pic = request.GET.get('profile_pic')
    cover_pic = request.GET.get('cover_pic')

    my_date = None
    if date:
        year, month, day = date.split('-')
        my_date = datetime.date(int(year), int(month), int(day))
    filters = [poll, date, image, video, album, profile_pic, cover_pic]
    search = False
    my_search_posts = ''
    posts = ''
    if any(filters):
        search = True
        if date and poll:
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                created_at__date=my_date, poll_post=True)
        elif date and image:
            medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                created_at__date=my_date, 
                                id__in=medias)
        elif date and video:
            medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                created_at__date=my_date, 
                                id__in=medias)
        elif date and album:
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                created_at__date=my_date, album_post=True)
        elif date and profile_pic:
            search_post = Post.objects.filter(
                group_post=False,
                profile=profile,
                is_deleted=False,
                normal_post=True,
                profile_picture_post=True,
                created_at__date=my_date,

            )
        elif date and cover_pic:
            search_post = Post.objects.filter(
                profile=profile,
                is_deleted=False,
                cover_post=True,
                normal_post=True,
                created_at__date=my_date,
            )
        elif not date and poll:
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                poll_post=True)
        elif not date and image:
            medias = list(postmedia.exclude(post_image='').values_list('post__id', flat=True))
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,
                                id__in=medias)
        elif not date and album:
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                album_post=True)
        elif not date and video:
            medias = list(postmedia.exclude(post_video='').values_list('post__id', flat=True))
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False ,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                normal_post=True,
                                job_project_post=False,
                                is_deleted=False,             
                                id__in=medias)

        elif not date and profile_pic:
            search_post = Post.objects.filter(
                group_post=False,
                profile=profile,
                is_deleted=False,
                normal_post=True,
                profile_picture_post=True,
            )
        elif not date and cover_pic:
            search_post = Post.objects.filter(
                profile=profile,
                is_deleted=False,
                cover_post=True,
                normal_post=True,
            )
        else:
            search_post = Post.objects.filter(
                                group_post=False,
                                profile=profile,  
                                page_post=False, 
                                blog_post=False,
                                video_module=False,
                                property_post=False,
                                automotive_post=False,
                                classified_post=False,
                                group_banner=False,
                                page_banner=False,
                                story_post=False,
                                job_post=False,
                                job_project_post=False,
                                is_deleted=False,
                                normal_post=True,
                                created_at__date=my_date, 
                                album_post=False)
        paginator = Paginator(search_post, 20)
        page_number = request.GET.get('page')
        my_search_posts = paginator.get_page(page_number)
    else:
        all_post = Post.objects.filter(
                    is_deleted=False, 
                    profile=profile, 
                    group_post=False, 
                    page_post=False, 
                    blog_post=False,
                    video_module=False,
                    property_post=False,
                    automotive_post=False,
                    classified_post=False,
                    group_banner=False,
                    shared_post=False,
                    page_banner=False,
                    story_post=False,
                    job_post=False,
                    normal_post=True,
                    job_project_post=False,
                                        ).order_by('-created_at')
        paginator = Paginator(all_post, 50)
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)
    context={
        'posts':posts,
        'search':search,
        'my_search_posts':my_search_posts,
        'front_end_server':front_end_server,

    }
    return render(request, 'adminpanel/total_post_of_single_user.html', context)

#admin delete single user posts
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_single_user_post(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        post1 = Post.objects.get(pk=id, is_deleted=False)
        post1.is_deleted = True
        post1.save()            
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin panel view album
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_album(request):
    total_album = UserAlbum.objects.filter(is_deleted=False).order_by('-created_at')
    full_path = 'album'
    paginator = Paginator(total_album, 50)
    page_number = request.GET.get('page')
    album = paginator.get_page(page_number)
    context = {
        'album':album,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/total_album.html', context)

# admin panel search album
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_album(request):
    get_title = request.GET.get('title')
    get_username = request.GET.get('username')
    title = get_title.strip()
    username = get_username.strip()
    full_path = 'album'
    if not title:
        title = ''
    if not username:
        username = ''

    total_search_album = UserAlbum.objects.filter(Q(album_title__icontains=title) &
                                Q(profile__user__username__icontains=username),
                                is_deleted=False)
    paginator = Paginator(total_search_album, 20)
    page_number = request.GET.get('page')
    album = paginator.get_page(page_number)
    context = {
        'album':album,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/search_album.html', context)

# admin panel delete album
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_album(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        album1 = UserAlbum.objects.get(pk=id, is_deleted=False)
        album_post = AlbumPost.objects.filter(album=album1)
        for ap in album_post:
            ap.post.is_deleted = True
            ap.post.save()
        album1.is_deleted = True
        album1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_groups(request):
    all_group = Group.objects.filter(is_deleted=False).order_by('-created_at')
    group_category = GroupCategory.objects.all()
    paginator = Paginator(all_group, 50)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'groups': groups,
        'group_category':group_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_group.html', context)

# admin search group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_group(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    get_admin = request.GET.get('admin')
    category = request.GET.get('category')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_groups = Group.objects.filter(Q(name__icontains=name) &
                            Q(category__title__icontains=category) &
                            Q(created_by__user__username__icontains=admin), 
                            is_deleted=False)
    paginator = Paginator(all_groups, 20)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)

    context = {
        'groups': groups,
        'group_category':group_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_group.html', context)

# admin delete group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_group(request):
    if request.method == 'POST':
        id = request.POST.get('gid')
        group1 = Group.objects.get(pk=id, is_deleted=False)
        group1.is_deleted = True
        group1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view  unpromoted group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_group(request):
    all_groups = Group.objects.filter(
                        is_promoted=False, 
                        is_deleted=False).order_by('-created_at')
    group_category = GroupCategory.objects.all()
    paginator = Paginator(all_groups, 50)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)
    context={
        'groups':groups,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/total_unpermoted_group.html', context)

# admin promote group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_group(request):
    if request.method == 'POST':
        id = request.POST.get('gid')
        group1 = Group.objects.get(
                        pk=id,
                        is_promoted=False,
                        is_deleted=False)
        group1.is_promoted = True
        group1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin search unpromoted group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_group(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_groups = Group.objects.filter(
                            Q(name__icontains=name) &
                            Q(category__title__icontains=category) &
                            Q(created_by__user__username__icontains=admin), 
                            is_deleted=False, is_promoted=False)
    paginator = Paginator(all_groups, 20)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)
    context = {
        'groups': groups,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/search_unpermote_group.html', context)

# admin view  promoted group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_group(request):
    group_category = GroupCategory.objects.all()
    all_groups = Group.objects.filter(is_promoted=True, is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_groups, 50)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)
    context = {
        'groups':groups,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/total_permoted_group.html', context)

# admin search promoted group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_group(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_groups = Group.objects.filter(
                            Q(name__icontains=name) &
                            Q(category__title__icontains=category) &
                            Q(created_by__user__username__icontains=admin), 
                            is_deleted=False, is_promoted=True)
    paginator = Paginator(all_groups, 20)
    page_number = request.GET.get('page')
    groups = paginator.get_page(page_number)
    context = {
        'groups': groups,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/search_permote_group.html', context)

# admin delete promoted group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_promoted_group(request):
    if request.method == 'POST':
        id = request.POST.get('gid')
        group1 = Group.objects.get(
                        pk=id, 
                        is_deleted=False, 
                        is_promoted=True)
        group1.is_deleted = True
        group1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view group post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_group_post(request, id):
    group = Group.objects.get(id=id, is_deleted=False)
    front_end_server = settings.FRONTEND_SERVER_NAME
    get_admin = request.GET.get('admin')
    search = False
    search_my_group_posts = ''
    group_posts = ''
    if get_admin:
        admin = get_admin.strip()
    else:
        admin = ''

    if admin:
        search = True
        search_group_posts = Post.objects.filter(
                            Q(profile__user__username__icontains=admin),
                            group_post=True, group=group, 
                            is_deleted=False)
        paginator = Paginator(search_group_posts, 20)
        page_number = request.GET.get('page')
        search_my_group_posts = paginator.get_page(page_number)
    else:
        all_group_posts = Post.objects.filter(
                            group_post=True,
                            group=group,  
                            is_deleted=False).order_by('-created_at')
        paginator = Paginator(all_group_posts, 50)
        page_number = request.GET.get('page')
        group_posts = paginator.get_page(page_number)
    context={
        'group_posts':group_posts,
        'search':search,
        'search_my_group_posts':search_my_group_posts,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_group_post.html', context)

# admin delete group post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_group_post(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        group_post1 = Post.objects.get(
                            pk=id, 
                            group_post=True, 
                            is_deleted=False)
        group_post1.is_deleted = True
        group_post1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view pages
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_pages(request):
    group_category = GroupCategory.objects.all()
    all_pages = Page.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_pages, 50)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'pages':pages,
        'group_category':group_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_page.html', context)

# admin search page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_page(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_pages = Page.objects.filter(
                            Q(name__icontains=name) &
                            Q(category__title__icontains=category) &
                            Q(created_by__user__username__icontains=admin), 
                            is_deleted=False)
    paginator = Paginator(all_pages, 20)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    context = {
        'pages': pages,
        'group_category':group_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_page.html', context)

# admin delete page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_page(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        page1 = Page.objects.get(pk=id, is_deleted=False)
        page1.is_deleted = True
        page1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view unpromote page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_page(request):
    group_category = GroupCategory.objects.all()
    all_pages = Page.objects.filter(is_deleted=False, is_promoted=False).order_by('-created_at')
    paginator = Paginator(all_pages, 50)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    context={
        'pages':pages,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/total_unpermote_page.html', context)

# admin search unpromote page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_page(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_pages = Page.objects.filter(Q(name__icontains=name) &
                                  Q(category__title__icontains=category) &
                                  Q(created_by__user__username__icontains=admin),
                                  is_promoted=False ,is_deleted=False)
    paginator = Paginator(all_pages, 20)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    context = {
        'pages': pages,
        'group_category':group_category,
        
    }
    return render(request, 'adminpanel/search_unpermote_page.html', context)

# admin promote group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_page(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        page1 = Page.objects.get(pk=id,is_promoted=False ,is_deleted=False)
        page1.is_promoted = True
        page1.save()
        
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view promote page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_page(request):
    group_category = GroupCategory.objects.all()
    all_pages = Page.objects.filter(is_deleted=False, is_promoted=True).order_by('-created_at')
    paginator = Paginator(all_pages, 50)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    context={
        'pages':pages,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/total_permote_page.html', context)

# admin search promote page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_page(request):
    group_category = GroupCategory.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_pages = Page.objects.filter(Q(name__icontains=name) &
                                  Q(category__title__icontains=category) &
                                  Q(created_by__user__username__icontains=admin),
                                  is_promoted=True ,is_deleted=False)
    paginator = Paginator(all_pages, 20)
    page_number = request.GET.get('page')
    pages = paginator.get_page(page_number)
    context = {
        'pages': pages,
        'group_category':group_category,
    }
    return render(request, 'adminpanel/search_permote_page.html', context)

# admin delete promote page
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_promoted_page(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        page1 = Page.objects.get(
                    pk=id, 
                    is_promoted=True,
                    is_deleted=False)
        page1.is_deleted = True
        page1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view page post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_page_post(request, id):
    page = Page.objects.get(id=id, is_deleted=False)
    get_admin = request.GET.get('admin')
    front_end_server = settings.FRONTEND_SERVER_NAME
    search_my_page_posts = ''
    page_posts = ''
    search = False
    if get_admin:
        admin = get_admin.strip()
    else:
        admin = ''
    if admin:
        search = True
        search_page_posts = Post.objects.filter(
                            Q(profile__user__username__icontains=admin),
                            page_post=True,
                            page=page, 
                            is_deleted=False)
        paginator = Paginator(search_page_posts, 20)
        page_number = request.GET.get('page')
        search_my_page_posts = paginator.get_page(page_number)
    else:
        all_page_posts = Post.objects.filter(
                            page_post=True, 
                            is_deleted=False, page=page).order_by('-created_at')
        paginator = Paginator(all_page_posts, 50)
        page_number = request.GET.get('page')
        page_posts = paginator.get_page(page_number)
    context = {
        'page_posts':page_posts,
        'search':search,
        'search_my_page_posts':search_my_page_posts,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_page_post.html', context)

# admin search page post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_page_post(request):
    get_admin = request.GET.get('admin')
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not admin:
        admin = ''
    all_page_posts = Post.objects.filter(
                            Q(profile__user__username__icontains=admin),
                            page_post=True, is_deleted=False)
        
    paginator = Paginator(all_page_posts, 20)
    page_number = request.GET.get('page')
    page_posts = paginator.get_page(page_number)
    context = {
        'page_posts': page_posts,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_page_post.html', context)

# admin delete page post
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_page_post(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        page_post1 = Post.objects.get(
                            pk=id, 
                            page_post=True,
                            is_deleted=False)
        page_post1.is_deleted = True
        page_post1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view properties
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_properties(request):
    property_category = Category.objects.all()
    all_properies = Property.objects.filter(
                            verification_status='Verified',
                            is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_properies, 50)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'properties':properties,
        'property_category':property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_property.html', context)

# admin search prpoperty
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_property(request):
    property_category = Category.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_properties = Property.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', is_deleted=False)
    paginator = Paginator(all_properties, 20)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    context = {
        'properties': properties,
        'property_category': property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_property.html', context)

# admin view pending properties
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_pending_properties(request):
    property_category = Category.objects.all()
    all_properies = Property.objects.filter(
                            verification_status='Pending',
                            is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_properies, 50)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'properties':properties,
        'property_category': property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_pending_property.html', context)

# admin accept property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_accept_pending_property(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        property1 = Property.objects.get(
                        pk=id,
                        verification_status='Pending',
                        is_deleted=False)
        property1.verification_status='Verified' 
        property1.save()
        
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin reject property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_reject_pending_property(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        property1 = Property.objects.get(
                            pk=id,
                            verification_status='Pending',
                            is_deleted=False)
        property1.verification_status='Rejected' 
        property1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin search pending prpoperty
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_pending_property(request):
    property_category = Category.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_properties = Property.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Pending', is_deleted=False)
    paginator = Paginator(all_properties, 20)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    context = {
        'properties': properties,
        'property_category':property_category,
    }
    return render(request, 'adminpanel/search_pending_property.html', context)

# admin delete property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_property(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        property1 = Property.objects.get(pk=id, is_deleted=False)
        property1.is_deleted = True
        property1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view unpromote properties
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_properties(request):
    property_category = Category.objects.all()
    all_properies=Property.objects.filter(
                            verification_status='Verified',
                            is_deleted=False, 
                            is_promoted=False).order_by('-created_at')
    paginator = Paginator(all_properies, 50)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'properties':properties,
        'property_category': property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_unpromote_property.html', context)

# admin search unpromote property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_property(request):
    property_category = Category.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_properties = Property.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', is_deleted=False, 
                                is_promoted=False)
    paginator = Paginator(all_properties, 20)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    context = {
        'properties': properties,
        'property_category': property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_unpromote_property.html', context)

# admin promote property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_property(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        property1 = Property.objects.get(
                            pk=id, 
                            is_promoted=False,
                            is_deleted=False)
        property1.is_promoted = True
        property1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view unpromote properties
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_properties(request):
    property_category = Category.objects.all()
    all_properies = Property.objects.filter(
                            verification_status='Verified',
                            is_deleted=False, 
                            is_promoted=True).order_by('-created_at')
    paginator = Paginator(all_properies, 50)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'properties':properties,
        'property_category':property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_promote_property.html', context)

# admin search property
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_property(request):
    property_category = Category.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_properties = Property.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', is_deleted=False, 
                                is_promoted=True)
    paginator = Paginator(all_properties, 20)
    page_number = request.GET.get('page')
    properties = paginator.get_page(page_number)
    context = {
        'properties': properties,
        'property_category': property_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_promote_property.html', context)

# admin promote group
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_promote_property(request):
    if request.method == 'POST':
        id = request.POST.get('pid')
        property1 = Property.objects.get(
                            pk=id, 
                            is_promoted=True,
                            is_deleted=False)
        property1.is_deleted = True
        property1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_automotives(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    all_automotives = Automotive.objects.filter(
                                verification_status='Verified',
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_automotives, 50)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'automotives':automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_automotive.html', context)

# admin search automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_automotive(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    brand = request.GET.get('brand')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    all_automotives=None
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    if not brand:
        brand = ''
    if brand and category:
        all_automotives = Automotive.objects.filter(
                                    Q(name__icontains=name) &
                                    Q(category__title=category) &
                                    Q(profile__user__username__icontains=admin)&
                                    Q(make__title=brand),
                                    verification_status='Verified', is_deleted=False)
    elif brand and not category:
        all_automotives = Automotive.objects.filter(
                                    Q(name__icontains=name) &
                                    Q(profile__user__username__icontains=admin)&
                                    Q(make__title=brand),
                                    verification_status='Verified', is_deleted=False)
    elif category and not brand:
        all_automotives = Automotive.objects.filter(
                                    Q(name__icontains=name) &
                                    Q(category__title=category) &
                                    Q(profile__user__username__icontains=admin),
                                    verification_status='Verified', is_deleted=False)
    else:
        all_automotives = Automotive.objects.filter(
                                    Q(name__icontains=name) &
                                    Q(profile__user__username__icontains=admin),verification_status='Verified', is_deleted=False)
    paginator = Paginator(all_automotives, 20)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    context = {
        'automotives': automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_automotive.html', context)

# admin view pending automotives
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_pending_automotives(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    all_automotives = Automotive.objects.filter(
                                verification_status='Pending',
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_automotives, 50)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'automotives':automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_pending_automotive.html', context)

# admin accept automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_accept_pending_automotive(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        automotive1 = Automotive.objects.get(
                                pk=id,
                                verification_status='Pending',
                                is_deleted=False)
        automotive1.verification_status='Verified' 
        automotive1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin reject automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_reject_pending_automotive(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        automotive1 = Automotive.objects.get(
                                pk=id,
                                verification_status='Pending',
                                is_deleted=False)
        automotive1.verification_status='Rejected' 
        automotive1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin search pending automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_pending_automotive(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    brand=request.GET.get('brand')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    if not brand:
        brand = ''
    all_automotives = Automotive.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(make__title__icontains=brand)&
                                Q(profile__user__username__icontains=admin),
                                verification_status='Pending', is_deleted=False)
    paginator = Paginator(all_automotives, 20)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    context = {
        'automotives': automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_pending_automotive.html', context)

# admin delete automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_automotive(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        automotive1 = Automotive.objects.get(pk=id, is_deleted=False)
        automotive1.is_deleted = True
        automotive1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view unpromote automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromoted_automotives(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    all_automotives = Automotive.objects.filter(
                                verification_status='Verified',
                                is_deleted=False, 
                                is_promoted=False).order_by('-created_at')
    paginator = Paginator(all_automotives, 50)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context=  {
        'automotives':automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_unpromote_automotive.html', context)

# admin search unpromote automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_automotive(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    brand = request.GET.get('brand')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    if not brand:
        brand = ''
    all_automotives = Automotive.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(make__title__icontains=brand)&
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', is_deleted=False, 
                                is_promoted=False)
    paginator = Paginator(all_automotives, 20)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    context = {
        'automotives': automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_unpromote_automotive.html', context)

# admin promote unpromted automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_automotive(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        automotive1 = Automotive.objects.get(
                            pk=id, 
                            is_deleted=False, 
                            is_promoted=False)
        automotive1.is_promoted = True
        automotive1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view promted automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promoted_automotives(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    all_automotives = Automotive.objects.filter(
                                verification_status='Verified', 
                                is_deleted=False, 
                                is_promoted=True).order_by('-created_at')
    paginator = Paginator(all_automotives, 50)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'automotives':automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_promote_automotive.html', context)

# admin search automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_automotive(request):
    automotive_category = AutomotiveCategory.objects.all()
    automotive_brand = AutomotiveMake.objects.all()
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    brand=request.GET.get('brand')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    if not brand:
        brand = ''
    all_automotives = Automotive.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(make__title__icontains=brand)&
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', is_deleted=False, 
                                is_promoted=True)
    paginator = Paginator(all_automotives, 20)
    page_number = request.GET.get('page')
    automotives = paginator.get_page(page_number)
    context = {
        'automotives': automotives,
        'automotive_category': automotive_category,
        'automotive_brand': automotive_brand,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_promote_automotive.html', context)

# admin delete unpromted automotive
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_promote_automotive(request):
    if request.method == 'POST':
        id = request.POST.get('aid')
        automotive1 = Automotive.objects.get(pk=id, is_deleted=False, is_promoted=True)
        automotive1.is_deleted = True
        automotive1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view classifed
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    all_classifieds = Classified.objects.filter(
                            verification_status='Verified',
                            business_directory=False,
                            is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_classifieds, 50)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'classifieds':classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_classified.html', context)

# admin search classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_classifieds = Classified.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', 
                                business_directory=False,
                                is_deleted=False)
    paginator = Paginator(all_classifieds, 20)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    context = {
        'classifieds': classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_classified.html', context)

# admin delete classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_classified(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        classified1 = Classified.objects.get(pk=id, business_directory=False, is_deleted=False)
        classified1.is_deleted = True
        classified1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view pending classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_pending_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    all_classifieds = Classified.objects.filter(
                                verification_status='Pending',
                                business_directory=False,
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_classifieds, 50)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'classifieds':classifieds,
        'classified_category': classified_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/total_pending_classified.html', context)

# admin search pending classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_pending_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_classifieds = Classified.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),verification_status='Pending', business_directory=False, is_deleted=False)
    paginator = Paginator(all_classifieds, 20)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    context = {
        'classifieds': classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_pending_classified.html', context)

# admin accept classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_accept_pending_classified(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        classified1 = Classified.objects.get(
                                pk=id,
                                verification_status='Pending',
                                business_directory=False,
                                is_deleted=False)
        classified1.verification_status='Verified' 
        classified1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin reject classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_reject_pending_classified(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        classified1 = Classified.objects.get(
                            pk=id,
                            verification_status='Pending',
                            business_directory=False,
                            is_deleted=False)
        classified1.verification_status='Rejected' 
        classified1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view unpromote classifed
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    all_classifieds = Classified.objects.filter(
                            verification_status='Verified',
                            is_deleted=False,
                            business_directory=False, 
                            is_promoted=False).order_by('-created_at')
    paginator = Paginator(all_classifieds, 50)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context={
        'classifieds':classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_unpromote_classified.html', context)

# admin search unpromote classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_classifieds = Classified.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),verification_status='Verified', 
                                is_deleted=False, 
                                business_directory=False,
                                is_promoted=False)
    paginator = Paginator(all_classifieds, 20)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    context = {
        'classifieds': classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_unpromote_classified.html', context)

# admin promote classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_classified(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        classified1 = Classified.objects.get(pk=id, verification_status='Verified', 
                                        is_deleted=False, 
                                        business_directory=False, 
                                        is_promoted=False)
        classified1.is_promoted=True
        classified1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view promote classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    all_classifieds=Classified.objects.filter(
                                    verification_status='Verified', 
                                    is_deleted=False,
                                    business_directory=False, 
                                    is_promoted=True).order_by('-created_at')
    paginator = Paginator(all_classifieds, 50)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'classifieds':classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/total_promote_classified.html', context)

# admin delete promote classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_promote_classified(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        classified1 = Classified.objects.get(pk=id, verification_status='Verified', 
                                        is_deleted=False,
                                        business_directory=False, 
                                        is_promoted=True)
        classified1.is_deleted = True
        classified1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin search promote classified
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_classified(request):
    classified_category = ClassifiedCategory.objects.filter(business_directory=False)
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip() 
    admin = get_admin.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    all_classifieds = Classified.objects.filter(
                                        Q(name__icontains=name) &
                                        Q(category__title__icontains=category) &
                                        Q(profile__user__username__icontains=admin),verification_status='Verified', 
                                        is_deleted=False,
                                        business_directory=False, 
                                        is_promoted=True)

    paginator = Paginator(all_classifieds, 20)
    page_number = request.GET.get('page')
    classifieds = paginator.get_page(page_number)
    context = {
        'classifieds': classifieds,
        'classified_category': classified_category,
        'front_end_server': front_end_server,
    }
    return render(request, 'adminpanel/search_promote_classified.html', context)

# admin view video
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_video(request):
    all_videos = Video.objects.filter(is_deleted=False).order_by('-created_at')
    video_category = VideoCategory.objects.all()
    paginator = Paginator(all_videos, 50)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME

    context={
        'videos':videos,
        'video_category':video_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/total_video.html', context)

# admin search video
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_video(request):
    video_category = VideoCategory.objects.all()
    get_title = request.GET.get('title')
    get_channel = request.GET.get('channel')
    get_username = request.GET.get('username')
    category = request.GET.get('category')
    title = get_title.strip() 
    channel = get_channel.strip()
    username = get_username.strip()
    front_end_server = settings.FRONTEND_SERVER_NAME

    if not title:
        title = ''
    if not channel:
        channel = ''
    if not category:
        category = ''
    if not username:
        username = ''
    all_videos = Video.objects.filter(
                                Q(title__icontains=title) &
                                Q(channel__name__icontains=channel) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=username),
                                is_deleted=False)

    paginator = Paginator(all_videos, 20)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)
    context = {
        'videos': videos,
        'video_category':video_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/search_video.html', context)

# admin view single video
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_single_video(request):
    if request.method == 'POST':
        id = request.POST.get('vid')
        videos = Video.objects.get(pk=id, is_deleted=False)
        return JsonResponse({"status":1})

# admin delete video
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_video(request):
    if request.method == 'POST':
        id = request.POST.get('vid')
        video1 = Video.objects.get(pk=id, is_deleted=False)
        video1.is_deleted = True
        video1.save()
        post = video1.post
        post.is_deleted = True
        post.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view video channel
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_video_channel(request):
    all_channels = VideoChannel.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_channels, 50)
    page_number = request.GET.get('page')
    channels = paginator.get_page(page_number)
    context = {
        'channels':channels,
    }
    return render(request, 'adminpanel/total_video_channel.html', context)

# admin search video channel
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_video_channel(request):
    get_channel_name = request.GET.get('channel_name')
    get_username = request.GET.get('username')
    date = request.GET.get('date')
    channel_name = get_channel_name.strip()
    username = get_username.strip()
    all_channels = ''
    if date:
        year, month, day = date.split('-')
        my_date=datetime.date(int(year), int(month), int(day))
    if date and  username and channel_name:
        all_channels = VideoChannel.objects.filter(
                                name__icontains=channel_name, 
                                created_at__date=my_date, 
                                profile__user__username__icontains=username, 
                                is_deleted=False)
    elif channel_name and  username and not date:
        all_channels = VideoChannel.objects.filter(
                                name__icontains=channel_name, 
                                profile__user__username__icontains=username, 
                                is_deleted=False)
    elif channel_name and  date and not username:
        channels = VideoChannel.objects.filter(
                                name__icontains=channel_name,
                                created_at__date=my_date, 
                                is_deleted=False)
    elif date and  username and not channel_name:
        all_channels = VideoChannel.objects.filter(
                                created_at__date=my_date, 
                                profile__user__username__icontains=username, 
                                is_deleted=False)
    elif channel_name and not date and not username:
        all_channels = VideoChannel.objects.filter(
                                name__icontains=channel_name, 
                                is_deleted=False)
    elif username and not date and not channel_name:
        all_channels = VideoChannel.objects.filter(
                                profile__user__username__icontains=username, 
                                is_deleted=False)
    elif date and not username and not channel_name:
        all_channels = VideoChannel.objects.filter(
                                created_at__date=my_date, 
                                is_deleted=False)
    paginator = Paginator(all_channels, 20)
    page_number = request.GET.get('page')
    channels = paginator.get_page(page_number)
    context = {
        'channels':channels,
    }
    return render(request, 'adminpanel/search_video_channel.html', context)

# admin delete video channels
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_video_channel(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        channel1 = VideoChannel.objects.get(is_deleted=False, pk=id)
        print(channel1)
        total_video = Video.objects.filter(is_deleted=False, channel=channel1)
        channel1.delete()
        total_video.delete()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view Jobs 
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_job(request):
    all_jobs = Job.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_jobs, 50)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'jobs':jobs,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/total_jobs.html', context)

# admin view Jobs 
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_job(request):
    get_title = request.GET.get('title')
    get_skill = request.GET.get('skill')
    title = get_title.strip()
    skill = get_skill.strip()

    if not title:
        title=''
    if not skill:
        skill=''

    if title or not skill:
        all_jobs = Job.objects.filter(
                            title__icontains=title,
                            is_deleted=False
                            )
    if skill:
        all_jobs = Job.objects.filter(
                            skill__skill__icontains=skill,
                            is_deleted=False
                            )
    if title and skill:
        all_jobs = Job.objects.filter(
                            title__icontains=title,
                            skill__skill__icontains=skill,
                            is_deleted=False
                            )
    paginator = Paginator(all_jobs, 20)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    context = {
        'jobs':jobs,
    }
    return render(request, 'adminpanel/search_jobs.html', context)

# admin delete jobs
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_job(request):
    if request.method == 'POST':
        id = request.POST.get('jid')
        job1 = Job.objects.get(is_deleted=False, pk=id)
        job1.is_deleted = True
        job1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view job profile
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_job_profile(request):
    job_profiles = JobProfile.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = Paginator(job_profiles, 50)
    page_number = request.GET.get('page')
    job_profiles = paginator.get_page(page_number)
    context = {
        'job_profiles':job_profiles,
    }
    return render(request, 'adminpanel/total_job_profiles.html', context)

# admin search job profile
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_job_profile(request):
    get_first_name = request.GET.get('first_name')
    get_last_name = request.GET.get('last_name')
    get_skill = request.GET.get('skill')
    first_name = get_first_name.strip()
    last_name = get_last_name.strip()
    skill = get_skill.strip()
    if not first_name:
        first_name = ''
    if not last_name:
        last_name = ''
    if not skill:
        skill = ''
    if skill:
        job_profiles = JobProfile.objects.filter(
                                first_name__icontains=first_name, 
                                last_name__icontains=last_name,
                                skill__skill__icontains=skill,
                                is_deleted=False)
    else:
        job_profiles = JobProfile.objects.filter(
                                first_name__icontains=first_name, 
                                last_name__icontains=last_name,
                                is_deleted=False)
    paginator = Paginator(job_profiles, 20)
    page_number = request.GET.get('page')
    job_profiles = paginator.get_page(page_number)
    context = {
        'job_profiles':job_profiles,
    }
    return render(request, 'adminpanel/search_job_profiles.html', context)

# admin delete job profile
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_job_profile(request):
    if request.method == 'POST':
        id = request.POST.get('jid')
        jobprofile1 = JobProfile.objects.get(is_deleted=False, pk=id)
        jobs = Job.objects.filter(jobprofile=jobprofile1,is_deleted=False)
        jobs.delete()
        jobprofile1.delete()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view signle jobs all apply
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_single_jobs_apply(request, id):
    try:
        job = Job.objects.get(id=id, is_deleted=False)
    except:
        pass
    all_job_applys = None
    get_full_name = request.GET.get('full_name')
    get_email = request.GET.get('email')
    get_mobile = request.GET.get('mobile')
    search_my_job_applys = ''
    job_applys = ''
    search = False
    if get_full_name:
        full_name = get_full_name.strip()
    else:
        full_name = ''

    if get_email:
        email = get_email.strip()
    else:
        email = ''
    
    if get_mobile:
        mobile = get_mobile.strip()
    else:
        mobile = ''

    filters = [full_name, email, mobile]

    if any(filters):
        search=True
        search_job_applys = JobApply.objects.filter(
                            full_name__icontains=full_name, 
                            email__icontains=email,
                            mobile__icontains= mobile,
                            job=job,
                            is_deleted=False)
        paginator = Paginator(search_job_applys, 20)
        page_number = request.GET.get('page')
        search_my_job_applys = paginator.get_page(page_number)
    else:
        all_job_applys = JobApply.objects.filter(job=job, is_deleted=False).order_by('-created_at')
        paginator = Paginator(all_job_applys, 50)
        page_number = request.GET.get('page')
        job_applys = paginator.get_page(page_number)

    context = {
        'job_applys':job_applys,
        'search':search,
        'search_my_job_applys':search_my_job_applys,
    }
    return render(request, 'adminpanel/total_apply_jobs.html', context)

# admin delete job apply
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_job_apply(request):
    if request.method == 'POST':
        id = request.POST.get('jid')
        jobapply1 = JobApply.objects.get(is_deleted=False, pk=id)
        jobapply1.is_deleted = True
        jobapply1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view blogs 
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_blog(request):
    all_blogs = Blog.objects.filter(is_deleted=False).order_by('-created_at')
    blog_category = BlogCategory.objects.all()
    paginator = Paginator(all_blogs, 50)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/total_blogs.html', context)

# admin delete blogs
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_blog(request):
    if request.method == 'POST':
        id = request.POST.get('bid')
        blog1 = Blog.objects.get(is_deleted=False, pk=id)
        blog1.is_deleted = True
        blog1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

#admin search blog 
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_blog(request):
    blog_category = BlogCategory.objects.all()
    get_title = request.GET.get('title')
    get_username = request.GET.get('username')
    get_category = request.GET.get('category')
    title = get_title.strip()
    username = get_username.strip()
    category = get_category.strip()

    if not title:
        title = ''
    if not username:
        username = ''
    if not category:
        category = ''
    if category or username or title:
        all_blogs = Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username ,
                            category__title__icontains=category,
                            is_deleted=False)
    elif  category:
        all_blogs = Blog.objects.filter(
                            category__title__icontains=category,
                            is_deleted=False)
    else:
        all_blogs = Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username ,
                            is_deleted=False)
    paginator = Paginator(all_blogs, 20)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/search_blogs.html', context)

# admin view unpromote blog
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_blog(request):
    blog_category = BlogCategory.objects.all()
    all_blogs = Blog.objects.filter(
                        is_promoted=False, 
                        is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_blogs, 50)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
    }
    return render(request, 'adminpanel/total_unpromoted_blog.html', context)

# admin search unpromote blog
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromoted_blog(request):
    blog_category = BlogCategory.objects.all()
    get_title = request.GET.get('title')
    get_username = request.GET.get('username')
    get_category = request.GET.get('category')
    title = get_title.strip()
    username = get_username.strip()
    category = get_category.strip()

    if not title:
        title = ''
    if not username:
        username = ''
    if not category:
        category = ''
    if category or username or title:
        all_blogs = Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username,
                            category__title__icontains=category,
                            is_deleted=False, 
                            is_promoted=False)
    elif  category:
        all_blogs = Blog.objects.filter(
                            category__title__icontains=category,
                            is_deleted=False, 
                            is_promoted=False)
    else:
        all_blogs = Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username,
                            is_deleted=False, 
                            is_promoted=False)
    paginator = Paginator(all_blogs, 20)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/search_unpromoted_blogs.html', context)

# admin promote blog
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_blog(request):
    if request.method == 'POST':
        id = request.POST.get('bid')
        blog1 = Blog.objects.get(is_deleted=False, pk=id, is_promoted=False)
        blog1.is_promoted = True
        blog1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin view promoted blog
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_blog(request):
    blog_category = BlogCategory.objects.all()
    all_blogs = Blog.objects.filter(
                    is_promoted=True, 
                    is_deleted=False).order_by('-created_at')
    paginator = Paginator(all_blogs, 50)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
    }
    return render(request, 'adminpanel/total_promoted_blog.html', context)

# admin search promoted blog
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promoted_blog(request):
    blog_category = BlogCategory.objects.all()
    get_title = request.GET.get('title')
    get_username = request.GET.get('username')
    get_category = request.GET.get('category')
    title = get_title.strip()
    username = get_username.strip()
    category = get_category.strip()

    if not title:
        title =''
    if not username:
        username =''
    if not category:
        category =''
    if category or username or title:
        all_blogs = Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username,
                            category__title__icontains=category,
                            is_deleted=False, 
                            is_promoted=True)
    elif  category:
        all_blogs = Blog.objects.filter(
                            category__title__icontains=category,
                            is_deleted=False,
                            is_promoted=True)
    else:
        all_blogs=Blog.objects.filter(
                            title__icontains=title,
                            profile__user__username__icontains=username, 
                            is_deleted=False, 
                            is_promoted=True)
    paginator = Paginator(all_blogs, 20)
    page_number = request.GET.get('page')
    blogs = paginator.get_page(page_number)
    front_end_server = settings.FRONTEND_SERVER_NAME
    context = {
        'blogs':blogs,
        'blog_category': blog_category,
        'front_end_server':front_end_server,
    }
    return render(request, 'adminpanel/search_promoted_blogs.html', context)

# admin panel view business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_business_directory(request):
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    full_path = 'business-directory/view'
    business_directory = Classified.objects.filter(
                                business_directory=True, 
                                verification_status='Verified', 
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(business_directory, 50)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business_category':business_category,
        'business':business,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/total_business_directory.html', context)

# admin panel search business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_business_directory(request):
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip()
    admin = get_admin.strip()
    full_path = 'business-directory/view'
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    business_directory = Classified.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', 
                                business_directory=True,
                                is_deleted=False)
    paginator = Paginator(business_directory, 20)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business': business,
        'business_category': business_category,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/search_business_directory.html', context)

# admin panel delete business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_delete_business_directory(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        business_directory1 = Classified.objects.get(pk=id, business_directory=True, is_deleted=False)
        business_directory1.is_deleted = True
        business_directory1.save()
        return JsonResponse({'status':True})
    return JsonResponse({'status':False})

# admin panel view pending business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_pending_business_directory(request):
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    full_path = 'business-directory/view'
    business_directory = Classified.objects.filter(
                                business_directory=True, 
                                verification_status='Pending', 
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(business_directory, 50)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business_category':business_category,
        'business':business,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/total_pending_business_directory.html', context)

# admin search pending business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_pending_business_directory(request):
    business_category = ClassifiedCategory.objects.filter(business_directory=False)
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip()
    admin = get_admin.strip()
    full_path = 'business-directory/view'
    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    business_directory = Classified.objects.filter(
                                Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Pending', 
                                business_directory=True, 
                                is_deleted=False)
    paginator = Paginator(business_directory, 20)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business': business,
        'business_category': business_category,
        'full_path': full_path,
    }
    return render(request, 'adminpanel/search_pending_business_directory.html', context)

# admin panel accept business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_accept_pending_business_directory(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        business_directory1 = Classified.objects.get(
                                pk=id,
                                verification_status='Pending',
                                business_directory=True,
                                is_deleted=False)
        business_directory1.verification_status = 'Verified'
        business_directory1.save()
        return JsonResponse({'status':True})
    return JsonResponse ({'status':False})

# admin panel reject business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_reject_pending_business_directory(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        business_directory1 = Classified.objects.get(
                                pk=id,
                                verification_status='Pending',
                                business_directory=True,
                                is_deleted=False)
        business_directory1.verification_status = 'Rejected'
        business_directory1.save()
        return JsonResponse({'status':True})
    return JsonResponse ({'status':False})

# admin panel view unpromoted business directory
login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_unpromote_business_directory(request):
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    full_path = 'business-directory/view'
    business_directory = Classified.objects.filter(
                                business_directory=True, 
                                verification_status='Verified',
                                is_promoted=False, 
                                is_deleted=False).order_by('-created_at')
    paginator = Paginator(business_directory, 50)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business_category':business_category,
        'business':business,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/total_unpromote_business_directory.html', context)

# admin panel search unpromote business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_unpromote_business_directory(request):
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip()
    admin = get_admin.strip()
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    full_path = 'business-directory/view'

    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    business_directory = Classified.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', 
                                business_directory=True,
                                is_promoted=False,
                                is_deleted=False)
    paginator = Paginator(business_directory, 20)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business': business,
        'business_category': business_category,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/search_unpromote_business_directory.html', context)

# admin panel prompte business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_promote_business_directory(request):
    if request.method == 'POST':
        id = request.POST.get('cid')
        business_directory1 = Classified.objects.get(pk=id, 
                                        verification_status='Verified', 
                                        is_deleted=False, 
                                        business_directory=True, 
                                        is_promoted=False)
        business_directory1.is_promoted = True
        business_directory1.save()
        return JsonResponse({'status': True})
    return JsonResponse({'status': False})

# admin view promoted business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_view_promote_business_directory(request):
    business_category = ClassifiedCategory.objects.filter(business_directory=True)
    full_path = 'business-directory/view'
    business_directory = Classified.objects.filter(
                                        is_deleted=False, 
                                        business_directory=True,
                                        verification_status='Verified',
                                        is_promoted=True)
    paginator = Paginator(business_directory, 50)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business': business,
        'business_category': business_category,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/total_promote_business_directory.html', context)

# admin search promoted business directory
@login_required(login_url='admin_panel_login')
@superuser_required()
def admin_panel_search_promote_business_directory(request):
    get_name = request.GET.get('name')
    category = request.GET.get('category')
    get_admin = request.GET.get('admin')
    name = get_name.strip()
    admin = get_admin.strip()
    full_path = 'business-directory/view/'
    business_category = ClassifiedCategory.objects.filter(business_directory=True)

    if not name:
        name = ''
    if not category:
        category = ''
    if not admin:
        admin = ''
    business_directory = Classified.objects.filter(Q(name__icontains=name) &
                                Q(category__title__icontains=category) &
                                Q(profile__user__username__icontains=admin),
                                verification_status='Verified', 
                                business_directory=True,
                                is_promoted=True,
                                is_deleted=False)
    paginator = Paginator(business_directory, 20)
    page_number = request.GET.get('page')
    business = paginator.get_page(page_number)
    context = {
        'business_category':business_category,
        'business':business,
        'full_path':full_path,
    }
    return render(request, 'adminpanel/search_promote_business_directory.html', context)
