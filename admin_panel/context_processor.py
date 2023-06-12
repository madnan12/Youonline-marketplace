from django.conf import settings
from youonline_social_app.models import Profile, UserProfilePicture

def admin_profile_picture(request):
    s3_bucket_link = settings.S3_BUCKET_LINK
    profileimage = None
    try:
        profile = Profile.objects.get(user=request.user, user__is_active=True)
    except:
        profile = None
    if profile:
        try:
            profileimage = UserProfilePicture.objects.get(profile=profile, is_deleted=False)
        except UserProfilePicture.DoesNotExist :
            profileimage = ''
        except:
            pass
    else:
        profileimage = None
    
    # To view following we use these URL from live youonline for Admin panel
    
    group = 'groups'
    post = 'post'
    page = 'page'
    property ='properties/propertyDetails'
    automotive = 'automotives/automotiveDetails'
    classified = 'classified/view'
    job = 'jobs'
    blog = 'blogs'
    jobprofile = 'jobs/userprofile'
    front_end_server = settings.FRONTEND_SERVER_NAME
    
    return {
      'profileimage': profileimage,
      's3_bucket_link':s3_bucket_link,
      'post':post,
      'group':group,
      'page':page,
      'automotive':automotive,
      'classified':classified,
      'property':property,
      'job':job,
      'blog':blog,
      'jobprofile':jobprofile,
      'front_end_server':front_end_server,
    }
        

        