import os
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import csv
from rest_framework.authentication import get_authorization_header
from rest_framework import exceptions
from django.conf import settings
import jwt
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from geopy.distance import geodesic

from helpers.constant import ROLE_OWNER_HERITED


def send_custom_mail(subject, message, recipients):
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=recipients)


def check_token(request):

    auth_header = get_authorization_header(request)

    auth_data = auth_header.decode('utf-8')

    auth_token = auth_data.split(" ")

    if len(auth_token) != 2:
        raise exceptions.AuthenticationFailed('Token not Valid')

    token = auth_token[1]
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY2, algorithms='HS256')

        return payload

    except jwt.ExpiredSignatureError as ex:
        raise exceptions.AuthenticationFailed(
            'Token expired, login again')

    except jwt.DecodeError as ex:
        raise exceptions.AuthenticationFailed(
            'Token is invalid')


def recover_email(email, uncripted_code):
    send_custom_mail(
        subject="recover password",
        message=f"This the your code to recover the Password {uncripted_code},I'll be valid for one hour.",
        recipients=[email],
    )


def get_objet_summary(Object, start_date, end_date):

    return Object.objects.filter(created_at__gte=start_date,
                                 created_at__lte=end_date,
                                 )


first_hour_today = timezone.now().replace(hour=00, minute=00)


def date_diff(first_date, last_date):
    return abs(first_date.day-last_date.day)


def hour_diff(first_hour, last_hour):
    diff_1 = abs(first_hour-last_hour)
    return round(diff_1.total_seconds()/3600, 1)


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('documents/', filename)


def get_related_user(request):
    if request.user.role_name in ROLE_OWNER_HERITED:
        return request.GET.get("user_id", None)
    return request.user


def get_distance_gps(long1, lat1, long2, lat2):
    point1 = (lat1, long1)
    point2 = (lat2, long2)
    return geodesic(point1, point2).m
