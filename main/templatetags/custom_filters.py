from django import template
from django.contrib.auth.models import User
from main.models import Profile

register = template.Library()

#Get the profile picture of the post's creator
@register.filter
def get_profile_image_url(username):
    try:
        user = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user)
        if user_profile.profileimg:
            return user_profile.profileimg.url
    except:
        pass

    return None


