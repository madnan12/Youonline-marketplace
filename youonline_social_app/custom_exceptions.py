from operator import imod
from textwrap import indent
from urllib import request
from rest_framework.response import Response
from rest_framework.views import exception_handler
from django.http import JsonResponse
from rest_framework import status
import linecache
import sys
import traceback
import os
import json
import inspect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import datetime
from .models import ExceptionRecord


def CreateExceptionRecord(exc, context):
    tb = exc.__traceback__
    trace = []
    data={}
    while tb is not None:
        trace.append({
            "File Name": tb.tb_frame.f_code.co_filename,
            "Error Name": tb.tb_frame.f_code.co_name,
            "Line Number": tb.tb_lineno
        })
        tb = tb.tb_next

    time_now = str(datetime.datetime.now())
    data[time_now] = trace

    ExceptionRecord.objects.create(
        content=data,
    )



def custom_exception_handler(exc, context):
    
    CreateExceptionRecord(exc, context)

    handlers={
        "ValidationError":_handle_generic_error,
        "Http404":_handle_generic_error,
        "PermissionDenied":_handle_generic_error,
        "NotAuthenticated":handle_authentication_error,
    } 
    response=exception_handler(exc, context)

    exception_class=exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    if response is not None:
        response.data['status_code']=response.status_code


    if response is None:
        context = {
            'error': str(exc),
            'Line_no':traceback.format_exc()
        }
        response = Response({'error': str(exc), 'Line_no':traceback.format_exc()},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Getting Email ready
        html_template = render_to_string('email/u-exception-email.html',
                                     {'error': str(exc), 'Line_no': traceback.format_exc(), 'img_link': settings.DOMAIN_NAME})
        text_template = strip_tags(html_template)
        send_email = EmailMultiAlternatives(
            'YouOnline | Exception',
            text_template,
            settings.EMAIL_HOST_USER,
            [settings.ADMIN_EMAIL]
        )
        send_email.attach_alternative(html_template, "text/html")
        try:
            send_email.send(fail_silently=False)
        except Exception as e:
            print(e)

    # return response


def _handle_generic_error(exc, context, response):

    response.data={
        'detail':  response.data if response else '',
        # 'status_code':response.status_code
    }
    return response

def handle_authentication_error(exc, context, response):
   
    response.data= {
        'error':'Please Login to proceed!',
        'status_code':response.status_code
    }
    
    return response