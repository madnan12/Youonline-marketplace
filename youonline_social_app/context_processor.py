from django.conf import settings
from django.conf import settings
from youonline_social_app.models import Profile, UserProfilePicture

def front_end_url(request):
    Domain = settings.DOMAIN_NAME
    
    return {
      'Domain':Domain,
    }
        

        