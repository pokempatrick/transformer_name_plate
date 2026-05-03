from rest_framework.generics import GenericAPIView
from rest_framework import response, status, permissions, viewsets, filters
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
import random
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import action
from authentification.models import User
from authentification.filters import UserFilter
from helpers.constant import ROLE_ADMIN_HERITED
from helpers.permissions import HasAdminRole, HasOWNERRole, IsUserOwner
from helpers.utils import recover_email, check_token
from authentification.serializer import RegisterSerilizer, LoginSerilizer, UserSerialiser

# Create your views here.


class AuthUserAPIView(GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RegisterSerilizer

    def get(self, request):

        user = request.user

        serializer = self.serializer_class(user)
        return response.Response({'user': serializer.data}, status=status.HTTP_200_OK)


class ResgisterAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegisterSerilizer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(GenericAPIView):

    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerilizer

    def post(self, request):
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        user = authenticate(username=email, password=password)

        if user:
            serializer = self.serializer_class(user)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response({"message": "invalid credential, try again"}, status=status.HTTP_401_UNAUTHORIZED)


class EmailSign(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = UserSerialiser

    def post(self, request):
        email = request.data.get("email", None)
        user = User.objects.filter(email=email).first()

        if user:
            uncripted_code = random.randrange(1000, 9999)
            recover_email(email=user.email, uncripted_code=uncripted_code)
            code = make_password(str(uncripted_code))
            token = jwt.encode(
                {
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id,
                    'code': code,
                    'exp': datetime.utcnow()+timedelta(hours=1)
                }, settings.SECRET_KEY2, algorithm='HS256')

            return response.Response({
                "token": token,
                "message": "Code de vérification envoyé",
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return response.Response({"message": "The user does not exist"}, status=status.HTTP_401_UNAUTHORIZED)


class CodeVerification(GenericAPIView):

    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerilizer

    def post(self, request):

        payload = check_token(request)
        code = request.data.get("code", None)
        if check_password(code, payload['code']):
            user_id = payload['user_id']
            user = User.objects.get(id=user_id)
            if user:
                serializer = self.serializer_class(user)
                return response.Response(serializer.data, status=status.HTTP_200_OK)

            return response.Response({"message": "The user does not exist, try again."}, status=status.HTTP_401_UNAUTHORIZED)
        return response.Response({"message": "invalid code, try again."}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    # authentication_classes = ()
    permission_classes = (permissions.IsAuthenticated,
                          HasOWNERRole)

    filter_backends = (UserFilter,)
    serializer_class = UserSerialiser

    def get_queryset(self):
        return User.objects.all()

    def create(self, request):

        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(
                added_by=self.request.user.first_name,
                limited_access_date=self.request.user.limited_access_date
            )
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = self.get_object()
        serializer = self.serializer_class(
            user,
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user.first_name)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.serializer_class(
            user,
            data=request.data,
            partial=True,
            context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(updated_by=self.request.user.first_name)
            return response.Response(serializer.data, status=status.HTTP_200_OK)

        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            user.is_active = not user.is_active
            user.updated_by = self.request.user.first_name
            user.save()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return response.Response({"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'])
    def set_password(self, request, pk=None):
        """ change password for authenticate user """

        self.permission_classes = (IsUserOwner,)
        user = self.get_object()
        serializer = RegisterSerilizer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['password'])
            user.save()
            return response.Response({'message': 'password updated'})
        else:
            return response.Response(serializer.errors,
                                     status=status.HTTP_400_BAD_REQUEST)


class AccessDateAPIView(GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,
                          HasAdminRole)
    serializer_class = UserSerialiser

    def patch(self, request):
        limited_access_date = request.data.get("limited_access_date", None)

        if limited_access_date:
            User.objects.exclude(role_name__in=ROLE_ADMIN_HERITED).update(
                limited_access_date=limited_access_date)
            return response.Response(
                {"message": "limited access date updated"}, status=status.HTTP_200_OK)

        return response.Response(
            {"message": "the date is not valid"}, status=status.HTTP_400_BAD_REQUEST)
