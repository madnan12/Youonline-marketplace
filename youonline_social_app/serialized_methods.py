"""
Serializers are good for quick development.
However they are relatively slower compared to custom functions.
The functions in this file are used for Optimizing the response
for API calls.
"""

from email.headerregistry import ContentTransferEncodingHeader
from youonline_social_app.models import *
from video_app.models import *
from django.conf import settings


def serialized_post_profile(profile):
    try:
        user = User.objects.get(profile_user=profile)
    except:
        return None
    try:
        profile_picture = UserProfilePicture.objects.get(profile=profile).picture.picture.url
        profile_picture = str(profile_picture.replace("/media/", settings.S3_BUCKET_LINK))
    except:
        profile_picture = None
    return_dict = {
        'id': profile.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'profile_picture': profile_picture
    }
    return return_dict


def serialized_post_reactions(reactions):
    all_reactions = []
    for reaction in reactions:
        return_dict = {
            'id': reaction.id,
            'post': reaction.post.id,
            'profile': serialized_post_profile(reaction.profile),
            'type': reaction.type,
            'created_at': reaction.created_at,
        }
        all_reactions.append(return_dict)
    return all_reactions


def serialized_post_poll(poll):
    options = PollOption.objects.filter(poll=poll).prefetch_related('pollvote_option')
    options_list = []
    for option in options:
        voters = []
        for voter in option.pollvote_option.all():
            voter_dict = serialized_post_profile(voter.profile)
            voters.append(voter_dict)
        option_dict = {
            'id': option.id,
            'poll': option.poll.id,
            'option': option.option,
            'voters': voters,
            'total_votes': option.total_votes,
        }
        options_list.append(option_dict)
    return_dict = {
        'id': poll.id,
        'description': poll.description,
        'total_votes': poll.total_votes,
        'expire_at': poll.expire_at,
        'poll_options': options_list,
    }
    return return_dict


def serialized_profile_picture(profile_picture):
    return_dict = dict()
    if profile_picture.picture:
        return_dict["picture"] = f"{settings.S3_BUCKET_LINK}{profile_picture.picture}"
    else:
        return_dict["picture"] = None
    return_dict["id"] = profile_picture.post.id
    return [return_dict]


def serialized_cover_picture(cover_picture):
    return_dict = dict()
    if cover_picture.cover:
        return_dict["picture"] = f"{settings.S3_BUCKET_LINK}{cover_picture.cover}"
    else:
        return_dict["picture"] = None
    return_dict["id"] = cover_picture.post.id
    return [return_dict]


def serilaized_post_media(media):
    medias = []
    for obj in media:
        return_dict = dict()
        if obj.post_image:
            return_dict['post_image'] = f"{settings.S3_BUCKET_LINK}{obj.post_image}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        if obj.post_video:
            return_dict['post_video'] = f"{settings.S3_BUCKET_LINK}{obj.post_video}"
            if obj.vid_thumbnail:
                return_dict['video_thumbnail'] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
            else:
                return_dict['video_thumbnail'] = ''
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        if obj.post_audio:
            return_dict['post_audio'] = f"{settings.S3_BUCKET_LINK}{obj.post_audio}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        if obj.post_gif:
            return_dict['post_gif'] = obj.post_gif
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        if obj.background_image:
            return_dict['background_image'] = f"{settings.S3_BUCKET_LINK}{obj.background_image}"
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        if obj.background_color:
            return_dict['background_color'] = obj.background_color
            return_dict['id'] = obj.post.id
            if obj.sub_post:
                return_dict['media_post_id'] = obj.sub_post.id
            else:
                return_dict['media_post_id'] = obj.post.id
        medias.append(return_dict)
    return medias


def serialized_album_media(media):
    medias = []
    post_album = {
        "album": {
            "id": media.album.id,
            "profile": media.album.profile.id,
            "album_title": media.album.title,
            "privacy": media.album.privacy,
        },
        "media_posts": []
    }
    for obj in media:
        return_dict = {
            "id": obj.id,
            "album": obj.album.id,
            "post": obj.post.id,
            "description": obj.description
        }
        if obj.image:
            return_dict["image"] = f"{settings.S3_BUCKET_LINK}{obj.image}"
        else:
            return_dict["image"] = None
        if obj.video:
            return_dict["video"] = f"{settings.S3_BUCKET_LINK}{obj.video}"
        else:
            return_dict["video"] = None
        if obj.vid_thumbnail:
            return_dict["vid_thumbnail"] = f"{settings.S3_BUCKET_LINK}{obj.vid_thumbnail}"
        else:
            return_dict["vid_thumbnail"] = None
        post_album["media_posts"].append(return_dict)
    return medias

def serialized_picture(channel):
    try:
        picture = ChannelPicture.objects.get(channel=channel)
        if picture.picture:
            picture = f"{settings.S3_BUCKET_LINK}{picture.picture}"
        else:
            picture = None
    except:
        picture = None

def serialized_channel(channel):
    return_dict = {
        'id': channel.id,
        'slug': channel.slug,
        'profile': channel.profile.id,
        'name': channel.name,
        'description': channel.description,
        'created_at': channel.created_at,
        'picture': serialized_picture(channel)

    }
    return return_dict
