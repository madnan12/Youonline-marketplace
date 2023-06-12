import datetime
import json
import profile
from urllib import response
import jwt
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.exceptions import ValidationError
from youonline_social_app.constants import *
from youonline_social_app.decorators import *
from django.db.models import Q
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.html import strip_tags
from youonline_social_app.models import Profile
from . models import *
from .models import ChatParticipant as ChatsParticipant
from . serializers import *
from youonline_social_app.serializers.post_serializers import *
from youonline_social_app.custom_api_settings import CustomPagination
from django.shortcuts import HttpResponse
from itertools import chain
from operator import attrgetter
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
from fcm_django.models import FCMDevice
from PIL import Image
from django.conf import settings
import threading
from datetime import timedelta
from chat_app.chat_threads import SendMessageThread, SendPostInMessageThread, ForwardChatMessageThread
from youonline_social_app.websockets.Constants import delete_chat_message_ws, send_chat_message_ws


# Create your views here.



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_individual_chat(request):
	profile2 = request.data['profile2'] if 'profile2' in request.data else None
	if not profile2:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
				status=status.HTTP_400_BAD_REQUEST)
	try:
		profile1 = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	try:
		profile2 = Profile.objects.get(id=profile2, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatParticipant.objects.get(
			Q(chat__created_by=profile1, profile=profile2, chat__chat_type='Individual') |
			Q(chat__created_by=profile2, profile=profile1, chat__chat_type='Individual')
		)
	except ObjectDoesNotExist:
		chat_participant = None
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_400_BAD_REQUEST)
	if chat_participant == None:
		chat = Chat.objects.create(
				created_by = profile1
			)
		# Add Creator to the chat
		try:
			chat_participant1 = ChatParticipant.objects.create(
					chat = chat,
					profile = profile1,
					created_by = profile1
				)
		except:
			pass
		# Add Other user to the Chat
		try:
			chat_participant2 = ChatParticipant.objects.create(
					chat = chat,
					profile = profile2,
					created_by = profile1
				)
		except:
			pass
		serializer = GetChatSerializer(chat, context={"profile": profile1})
		return Response({"success": True, 'response': serializer.data},
						status=status.HTTP_201_CREATED)
	else:
		for i in ChatParticipant.objects.filter(chat=chat_participant.chat):
			i.is_deleted = False
			i.save()
		serializer = GetChatSerializer(chat_participant.chat)
		return Response({"success": True, 'response': serializer.data},
							status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_chatslist(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)

	chat_ids = ChatParticipant.objects.filter(
		profile=profile, 
		chat__is_deleted=False,
		is_archived=False,
		is_deleted=False
	).values_list('chat__id', flat=True)
	chats = Chat.objects.filter(
		Q(id__in=chat_ids, chat_type='Individual', last_message__isnull=False, last_message__is_deleted=False) |
		Q(id__in=chat_ids, chat_type='Group', last_message__is_deleted=False),
	).order_by('-last_message__created_at')
	
	context = {
		'profile': profile,
	}
	serializer = ChatListSerializer(chats, many=True, context=context)
	return Response({"success": True, 'response':  serializer.data},
				status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def block_chat(request):
	try:
		user_profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)

	chat_id = request.GET.get('chat' , None)
	if chat_id is None:
		return Response({"success": False, 'response': {'message': 'Invalid Data'}},
				status=status.HTTP_400_BAD_REQUEST)

	try:
		chat = Chat.objects.get(id=chat_id, is_deleted=False)
	except :
		return Response({"success": False, 'response': {'message': 'Chat not found'}},
				status=status.HTTP_404_NOT_FOUND)

	chat.blocked_by = user_profile
	chat.save()
	return Response({"success": True, 'response': {'message': 'Blocked successfully'}},
				status=status.HTTP_200_OK)
	
	

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unblock_chat(request):
	try:
		user_profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)

	chat_id = request.GET.get('chat' , None)
	if chat_id is None:
		return Response({"success": False, 'response': {'message': 'Invalid Data'}},
				status=status.HTTP_400_BAD_REQUEST)

	try:
		chat = Chat.objects.get(id=chat_id, is_deleted=False, blocked_by=user_profile)
	except :
		return Response({"success": False, 'response': {'message': 'Chat not found'}},
				status=status.HTTP_404_NOT_FOUND)

	chat.blocked_by = None
	chat.save()
	return Response({"success": True, 'response': {'message': 'Unblocked successfully'}},
				status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat(request):
	chat = request.query_params.get('chat')
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		participant = ChatParticipant.objects.get(chat=chat, profile=profile)
	except ObjectDoesNotExist:
		return Response({"success": False, 'response': {'message': "You don't have the permissions to view this chat."}},
					status=status.HTTP_403_FORBIDDEN)
	except:
		pass


	paginator = CustomPagination()
	paginator.page_size = 25
	result_page = paginator.paginate_queryset(chat.chatmessage_chat.all().exclude(deleted_by=profile).order_by('created_at')[::-1], request)
	serializer = GetChatMessageSerializer(result_page, many=True, context={"request": request, "profile": profile})
	return paginator.get_paginated_response(serializer.data[::-1])


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_chat_message(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	receiver = request.data['profile'] if 'profile' in request.data else None

	text = request.data['text'] if 'text' in request.data else ''
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	try:
		receiver = Profile.objects.get(id=receiver, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		participant = ChatParticipant.objects.get(chat=chat, profile=profile)
	except:
		return Response({"success": False, 'response': {'message': 'You are not allowed to send message to this chat.'}},
					status=status.HTTP_400_BAD_REQUEST)
	if chat.chat_type == 'Individual':
		chat_participants = ChatParticipant.objects.filter(chat=chat)
		for i in chat_participants:
			i.is_deleted = False
			removed_by = None
			i.save()
	
	try:
		request.data._mutable = True
	except:
		pass
	request.data['profile'] = profile.id
	serializer = ChatMessageSerializer(data=request.data)
	if serializer.is_valid():
		chat_message = serializer.save()
		# Set Last Message time here.
		chat.last_message = chat_message
		# for i in receiver:
		chat_message.delivered_to.add(receiver)
		chat.save()
		# Send Message To Firestore using thread
		SendMessageThread(request, chat_message, profile, chat).start()

		serializer = GetChatMessageSerializer(chat_message)
		user_chat = GetChatSerializerSocket(chat).data
		send_chat_message_ws(request, serializer.data, profile, user_chat, receiver)

		# Creating Notification for Automotive 
		notification_user = chat_message.delivered_to.all()
		# for i in notification_user:
		# 	if i.id != profile.id:
		notification = Notification(
		type = 'Chat',
		profile = profile,
		text = f'{profile.user.first_name} sent you a message.',
		)
		notification.save()
		notification.notifiers_list.add(receiver)
		notification.save()
		try:
			send_notifications_ws(notification)
		except:
			pass
			# End Notification
			
		return Response({"success": True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)
	else:
		return Response({"success": False, 'response': {'message': serializer.errors}},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_post_in_chat(request):
	post = request.data['post'] if 'post' in request.data else None
	chat = request.data['chat'] if 'chat' in request.data else None
	text = request.data['text'] if 'text' in request.data else None

	if not post and not chat:
		return Response({'success': False, 'response': {'message': 'Invalid data!'}},
					status=status.HTTP_400_BAD_REQUEST)
	else:
		try:
			post = Post.objects.get(id=post, is_deleted=False)
		except:
			return Response({'success': False, 'response': {'message': 'Post not found!'}},
						status=status.HTTP_404_NOT_FOUND)
		try:
			profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
		except Exception as e:
			return Response({"success": False, 'response': {'message': str(e)}},
							status=status.HTTP_401_UNAUTHORIZED)
		try:
			chat = Chat.objects.get(id=chat, is_deleted=False)
		except Exception as e:
			return Response({'success': False, 'response': {'message': str(e)}},
						status=status.HTTP_404_NOT_FOUND)
		try:
			chat_participant = ChatParticipant.objects.get(
				chat = chat,
				profile = profile,
				is_deleted = False
			)
		except:
			try:
				chat_participant = ChatParticipant.objects.get(
						chat = chat,
						profile = profile,
					)
				chat_participant.is_deleted = False
				chat_participant.removed_by = None
				chat_participant.save()
			except:
				return Response({'success': False, 'response': {'message': 'You are not allowed to send message to this chat.'}},
						status=status.HTTP_404_NOT_FOUND)
		serializer = ChatMessageSerializer(data=request.data)
		if serializer.is_valid():
			chat_message = serializer.save()
			# Set Post for message.
			if post:
				chat_message.post = post
				chat_message.post_message = True
				chat_message.save()
			# Set Last Message here.
			chat.last_message = chat_message
			chat.save()
			# Send Message to Firestore using thread
			SendPostInMessageThread(request, chat_message, chat, profile).start()

			serializer = GetChatMessageSerializer(chat_message)
			return Response({"success": True, 'response': {'message': serializer.data}},
						status=status.HTTP_201_CREATED)
		else:
			return Response({"success": False, 'response': {'message': serializer.errors}},
						status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_group_chat(request):
	try:
		created_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_401_UNAUTHORIZED)
	request.data._mutable = True
	request.data['created_by'] = created_by.id
	members = request.data['members'] if 'members' in request.data else None
	title = request.data['title'] if 'title' in request.data else None
	if not title or not members:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	else:
		serializer = ChatSerializer(data=request.data)
		if serializer.is_valid():
			chat = serializer.save()
			ChatParticipant.objects.create(
					chat = chat,
					profile = chat.created_by,
					created_by = chat.created_by,
				)
			members = members[1:-1].replace('"', "").split(',')
			for i in members:
				try:
					profile = Profile.objects.get(id=i)
					ChatParticipant.objects.create(
							chat = chat,
							profile = profile,
							created_by = chat.created_by,
						)
				except:
					pass
			serializer = GetChatSerializer(chat, context={"profile": chat.created_by})
			return Response({"success": True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)
		else:
			return Response({"success": False, 'response': {'message': serializer.errors}},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_group_chat_member(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	profile = request.data['profile'] if 'profile' in request.data else None
	try:
		created_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat or not profile:
		return Response({"success": False, 'response': {'message': 'Invalid Data'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	if chat.created_by != created_by:
		return Response({"success": False, 'response': {'message': 'You are not allowed to add members to this chat.'}},
					status=status.HTTP_400_BAD_REQUEST)
	if chat.chat_type != 'Group':
		return Response({"success": False, 'response': {'message': 'You cannot add a member to an Individual Chat.'}},
					status=status.HTTP_403_FORBIDDEN)
	try:
		chat_participant = ChatParticipant.objects.get(
			chat = chat,
			profile = profile,
			is_deleted = False
		)
		return Response({"success": False, 'response': {'message': 'Member already added in chat!'}},
					status=status.HTTP_400_BAD_REQUEST)
	except:
		try:
			chat_participant = ChatParticipant.objects.get(
					chat = chat,
					profile = profile,
				)
			chat_participant.is_deleted = False
			chat_participant.removed_by = None
			chat_participant.save()
		except:
			chat_participant = ChatParticipant.objects.create(
					chat = chat,
					profile = profile,
					created_by = created_by
				)
		return Response({"success": True, 'response': {'message': 'Member added to the chat successfully!'}},
					status=status.HTTP_201_CREATED)
	

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_group_chat_member(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	profile = request.data['profile'] if 'profile' in request.data else None
	try:
		removed_by = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat or not profile:
		return Response({"success": False, 'response': {'message': 'Invalid Data'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(id=profile, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	if chat.created_by != removed_by and profile != removed_by:
		return Response({"success": False, 'response': {'message': 'You are not allowed to remove this member from chat.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat_participant = ChatParticipant.objects.get(
				chat = chat,
				profile = profile,
				is_deleted = False
			)
		chat_participant.is_deleted = True
		chat_participant.deleted_at = datetime.datetime.now()
		chat_participant.removed_by = removed_by
		chat_participant.save()
		try:
			del_chat = ChatDeletionTracker.objects.get(
					profile=profile,
					chat=chat
				)
			del_chat.deleted_at = datetime.datetime.now()
			del_chat.save()
		except:
			del_chat = ChatDeletionTracker.objects.create(
					profile=profile,
					chat=chat,
					deleted_at=datetime.datetime.now()
				)
		return Response({"success": True, 'response': {'message': 'Member removed from chat successfully!'}},
					status=status.HTTP_201_CREATED)
	except Exception as e:
		return Response({"success": False, 'response': {'message': 'Member not a member of chat already.'}},
					status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat_message(request):
	chat_message = request.data['chat_message'] if 'chat_message' in request.data else None
	delete_for = request.data['delete_for'] if 'delete_for' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat_message or not delete_for:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat_message = ChatMessage.objects.get(id=chat_message, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)

	# if chat_message.profile != profile:
	# 	return Response({"success": False, 'response': {'message': "You don't have the access to delete this message."}},
	# 				status=status.HTTP_403_FORBIDDEN)

	if chat_message.profile == profile:
		if delete_for == 'Foreveryone':
			chat_message.is_deleted = True
			for prf in chat_message.chat.chatparticipant_chat.all():
				chat_message.deleted_by.add(prf.profile)
			chat_message.deleted_at = datetime.datetime.now()
			# settings.FIRESTORE.collection(str(chat_message.chat.id)).document(str(chat_message.id)).delete()
			try:
				delete_chat_message_ws(request, chat_message.id, profile, chat_message.chat)
			except Exception as err:
				print(err)
		elif delete_for == 'Forme':
			chat_message.deleted_by.add(profile)
		else:
			pass
	elif delete_for == 'Forme':
		chat_message.deleted_by.add(profile)
	else:
		return Response({"success": False, 'response': {'message': 'You dont have the access to delete this message for everyone!'}},
					status=status.HTTP_400_BAD_REQUEST)

	# Delete Message from FireStore
	# if chat_message.deleted_by and not chat_message.is_deleted:
	# 	del_message_fs = settings.FIRESTORE.collection(str(chat_message.chat.id)).document(str(chat_message.id))
	# 	del_message_fs.set({
	# 		u'deleted_by' : DefaultProfileSerializer(chat_message.deleted_by.all(), many=True).data
	# 	} , merge=True)
	chat_message.save()

	chat = chat_message.chat
	all_messages_list = ChatMessage.objects.filter(is_deleted=False , chat=chat).order_by('-created_at')
	if len(all_messages_list) > 0:
		chat.last_message = all_messages_list[0]
	else:
		chat.last_message = None
	chat.save()
	return Response({"success": True, 'response': {'message': "Message deleted successfully."}},
					status=status.HTTP_200_OK)


class ChatDeleteThread(threading.Thread):

	def __init__(self, chat, profile):
		self.chat = chat
		self.profile = profile
		threading.Thread.__init__(self)

	def run(self):
		chat_messages = ChatMessage.objects.filter(chat=self.chat)
		for i in chat_messages:
			i.deleted_by.add(self.profile)
			i.save()
			# Add all the delete profiles to Firebase.
			# profiles = i.deleted_by.all()
			# doc_ref = settings.FIRESTORE.collection(str(self.chat.id)).document(str(i.id))
			# doc_ref.set({
			# 	u'deleted_by': DefaultProfileSerializer(profiles, many=True).data
			# }, merge=True)
		print("++++++++++ Delete Chat Thread Run successfully")


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_chat(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	# Check if chat exists
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	# Check if the user is part of the chat.
	try:
		chat_participant = ChatParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
	except ObjectDoesNotExist:
		return Response({"success": False, 'response': {'message': "You don't have the permissions to delete this chat"}},
					status=status.HTTP_403_FORBIDDEN)
	# Delete the chat.
	if chat.chat_type == 'Individual':
		chat_participant.is_deleted = True
		chat_participant.removed_by = profile
		chat_participant.save()
	ChatDeleteThread(chat, profile).start()
	return Response({"success": True, 'response': {'message': 'Chat deleted successfully.'}},
				status=status.HTTP_200_OK)
	

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def archive_chat(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
	except ObjectDoesNotExist:
		return Response({"success": False, 'response': {'message': "You are not added to this chat."}},
					status=status.HTTP_403_FORBIDDEN)
	if chat_participant.is_archived:
		chat_participant.is_archived=False
		chat_participant.save()
		return Response({"success": True, 'response': {'message': 'Unarchived'}},
						status=status.HTTP_200_OK)
	else:
		chat_participant.is_archived=True
		chat_participant.save()
		return Response({"success": True, 'response': {'message': 'Archived'}},
						status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_archived_chats(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	chat_ids = ChatParticipant.objects.filter(profile=profile, chat__is_deleted=False, is_archived=True).values_list('chat__id', flat=True)
	chats = Chat.objects.filter(id__in=chat_ids).select_related('last_message', 'last_message__profile').order_by('-last_message__created_at')
	serializer = ChatListSerializer(chats, many=True)
	return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)
	

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mute_chat(request):
	chat = request.data['chat'] if 'chat' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
	except ObjectDoesNotExist:
		return Response({"success": False, 'response': {'message': "You are not added to this chat."}},
					status=status.HTTP_403_FORBIDDEN)
	if chat_participant.is_muted:
		chat_participant.is_muted=False
		chat_participant.save()
		return Response({"success": True, 'response': {'message': 'Unmuted'}},
						status=status.HTTP_200_OK)
	else:
		chat_participant.is_muted=True
		chat_participant.save()
		return Response({"success": True, 'response': {'message': 'Muted'}},
						status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_muted_chats(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	chat_ids = ChatParticipant.objects.filter(profile=profile, chat__is_deleted=False, is_muted=True).values_list('chat__id', flat=True)
	chats = Chat.objects.filter(id__in=chat_ids)
	serializer = ChatListSerializer(chats, many=True)
	return Response({"success": True, 'response': {'message': serializer.data}},
				status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_chat_message(request):
	chat = request.query_params.get('chat')
	text = request.query_params.get('text')
	if not chat or not text:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	chat_messages = ChatMessage.objects.filter(text__icontains=text).exclude(deleted_by=profile).order_by('-created_at')
	serializer = GetChatMessageSerializer(chat_messages, many=True)
	return Response({"success": True, 'response': {'message': serializer.data}},
					status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def forward_chat_message(request):
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	chat = request.data['chat'] if 'chat' in request.data else None
	chat_message = request.data['chat_message'] if 'chat_message' in request.data else None
	if not chat or not chat_message:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	# Check if Chat exists
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	# Check if Chat Message exists
	try:
		chat_message = ChatMessage.objects.get(id=chat_message, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	forward_message = ChatMessage.objects.create(
			chat=chat,
			profile=profile,
			text=chat_message.text,
			is_forwarded=True
		)
	message_medias = ChatMessageMedia.objects.filter(chat_message=chat_message, is_deleted=False)
	for i in message_medias:
		forward_message_media = ChatMessageMedia.objects.create(
				profile=profile,
				chat_message=forward_message,
				image=i.image,
				video=i.video,
				vid_thumbnail=i.vid_thumbnail,
				audio=i.audio,
				gif=i.gif,
			)
	chat.last_message = forward_message
	chat.save()
	print('/////////////// send' , chat.last_message)
	# Send Forward message to Firestore using threads.

	ForwardChatMessageThread(request, forward_message, profile, chat).start()
	serializer = GetChatMessageSerializer(forward_message)
	return Response({"success": True, 'response': {'message': serializer.data}},
					status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def read_chat_message(request):
	chat_message = request.data['chat_message'] if 'chat_message' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat_message:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat_message = ChatMessage.objects.get(id=chat_message, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	readers = list(ChatMessage.objects.filter(chat=chat_message.chat, is_deleted=False, read_by=profile).values_list('id', flat=True))
	chat_messages = ChatMessage.objects.filter(chat=chat_message.chat, is_deleted=False).exclude(id__in=readers)
	for i in chat_messages:
		i.read_by.add(profile)
		i.save()
		# Add read by to the FireStore
		read_bys = i.read_by.all()
		doc_ref = settings.FIRESTORE.collection(str(i.chat.id)).document(str(i.id))
		doc_ref.set({
			u'read_by': DefaultProfileSerializer(read_bys, many=True).data,
		}, merge=True)
	return Response({"success": True, 'response': {'message': "Message read successfully."}},
					status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def deliver_chat_message(request):
	chat_message = request.data['chat_message'] if 'chat_message' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat_message:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat_message = ChatMessage.objects.get(id=chat_message, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)

	chat_messages = ChatMessage.objects.filter(
		chat=chat_message.chat,
		created_at__lte=chat_message.created_at, 
		is_deleted=False
	).exclude(
		delivered_to=profile,
		profile=profile
	)

	for ctm in chat_messages:
		ctm.delivered_to.add(profile)
		ctm.save()
		# Add read by to the FireStore
		delivered_tos = ctm.delivered_to.all()
		doc_ref = settings.FIRESTORE.collection(str(ctm.chat.id)).document(str(ctm.id))
		doc_ref.set({
			u'delivered_to': DefaultProfileSerializer(delivered_tos, many=True).data,
		}, merge=True)
	return Response({"success": True, 'response': {'message': "Message delivered successfully."}},
					status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mute_user_chat(request):
	mute_duration = request.data['mute_duration'] if 'mute_duration' in request.data else None
	chat = request.data ['chat'] if 'chat' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat or not mute_duration:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False, chat_type='Individual')
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatsParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)

	current_time = datetime.datetime.now()
	fifteenmin = current_time + timedelta(minutes=15)
	onehour = current_time + timedelta(hours=1)
	eighthours = current_time + timedelta(hours=8)
	twentyfourhours = current_time + timedelta(hours=24)

	if mute_duration:
		if mute_duration == '15Min':
			chat_participant.is_muted = True
			chat_participant.muted_till = fifteenmin
			chat_participant.save()
		elif mute_duration == '1Hour':
			chat_participant.is_muted = True
			chat_participant.muted_till = onehour
			chat_participant.save()
		elif mute_duration == '8Hours':
			chat_participant.is_muted = True
			chat_participant.muted_till = eighthours
			chat_participant.save()
		elif mute_duration == '24Hours':
			chat_participant.is_muted = True
			chat_participant.muted_till = twentyfourhours
			chat_participant.save()
		elif mute_duration == 'always':
			chat_participant.is_muted = True
			chat_participant.muted_till = None
			chat_participant.save()
	serializer = ChatParticipantSerializer(chat_participant)
	return Response({"success": True, 'response': {'message': serializer.data}},
			status=status.HTTP_201_CREATED)
	

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mute_group_chat(request):
	mute_duration = request.data['mute_duration'] if 'mute_duration' in request.data else None
	chat = request.data ['chat'] if 'chat' in request.data else None
	try:
		profile = Profile.objects.get(user=request.user, is_deleted=False, user__is_active=True)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)
	if not chat or not mute_duration:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False, chat_type='Group')
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatsParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)

	current_time = datetime.datetime.now()
	fifteenmin = current_time + timedelta(minutes=15)
	onehour = current_time + timedelta(hours=1)
	eighthours = current_time + timedelta(hours=8)
	twentyfourhours = current_time + timedelta(hours=24)
	if mute_duration:
		if mute_duration == '15Min':
			chat_participant.is_muted = True
			chat_participant.muted_till = fifteenmin
			chat_participant.save()
		elif mute_duration == '1Hour':
			chat_participant.is_muted = True
			chat_participant.muted_till = onehour
			chat_participant.save()
		elif mute_duration == '8Hours':
			chat_participant.is_muted = True
			chat_participant.muted_till = eighthours
			chat_participant.save()
		elif mute_duration == '24Hours':
			chat_participant.is_muted = True
			chat_participant.muted_till = twentyfourhours
			chat_participant.save()
		elif mute_duration == 'always':
			chat_participant.is_muted = True
			chat_participant.muted_till = None
			chat_participant.save()
	serializer = ChatParticipantSerializer(chat_participant)
	return Response({"success": True, 'response': {'message': serializer.data}},
			status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unmute_user_chat(request):
	chat = request.data['chat'] if 'chat' in request.data else None	
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
			status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)	
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False, chat_type='Individual')
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
			status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatsParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
		chat_participant.is_muted = False
		chat_participant.muted_till = None
		chat_participant.save()
		serializer = ChatParticipantSerializer(chat_participant)
		return Response({"success": True, 'response': {'message': serializer.data}},
			status=status.HTTP_201_CREATED)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unmute_group_chat(request):
	chat = request.data['chat'] if 'chat' in request.data else None	
	if not chat:
		return Response({"success": False, 'response': {'message': 'Invalid Data.'}},
					status=status.HTTP_400_BAD_REQUEST)
	try:
		profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
						status=status.HTTP_401_UNAUTHORIZED)	
	try:
		chat = Chat.objects.get(id=chat, is_deleted=False, chat_type='Group')
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)
	try:
		chat_participant = ChatsParticipant.objects.get(chat=chat, profile=profile, is_deleted=False)
		chat_participant.is_muted = False
		chat_participant.muted_till = None
		chat_participant.save()
		serializer = ChatParticipantSerializer(chat_participant)
		return Response({"success": True, 'response': {'message': serializer.data}},
			status=status.HTTP_201_CREATED)
	except Exception as e:
		return Response({"success": False, 'response': {'message': str(e)}},
					status=status.HTTP_404_NOT_FOUND)

# @api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
# def delete_chat_message_one_side(request):
# 	chat_message = request.data['chat_message'] if 'chat_message' in request.data else None
# 	try:
# 		profile = Profile.objects.get(user=request.user, user__is_active=True, is_deleted=False)
# 	except Exception as e:
# 		return Response({"success":False, 'response':{'message': str(e)}},
# 					status=status.HTTP_401_UNAUTHORIZED)
# 	if not chat_message:
# 		return Response({"success":False, 'response':{'message':'Invalid Data!'}}, 
# 					status=status.HTTP_400_BAD_REQUEST) 
# 	try:
# 		chat_message = ChatMessage.objects.get(id=chat_message, is_deleted=False)
# 	except Exception as e:
# 		return Response({"success": False, 'response': {'message': str(e)}},
# 					status=status.HTTP_404_NOT_FOUND)
# 	chat_message.deleted_by.add(profile) 
# 	# settings.FIRESTORE.collection(str(chat_message.chat.id)).document(str(chat_message.id)).delete()
# 	chat_message.save()
# 	chat = chat_message.chat
# 	all_messages_list = ChatMessage.objects.filter(is_deleted=False, chat=chat).order_by('-created_at')
# 	if len(all_messages_list) > 0:
# 		chat.last_message = all_messages_list[0]
# 	else:
# 		chat.last_message = None
# 	chat.save()
# 	return Response({"success": True, 'response': {'message': "Message deleted successfully."}},
# 					status=status.HTTP_200_OK)