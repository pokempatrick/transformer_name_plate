from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from authentification.models import User


class RegisterSerilizer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "image")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerilizer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "token", "username",
                  "id", "role_name", "limited_access_date")

        read_only_fields = ["token", "id", "role_name", "limited_access_date"]


class UserSerialiser(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ("id", "email", "username", "last_name", "first_name", "image", "first_contact",
                  "second_contact", "created_at", "updated_at", "role_name", "added_by",
                  "updated_by", "limited_access_date", "is_active")
        read_only_fields = ['created_at',
                            'updated_at', "added_by", "updated_by", "limited_access_date", "is_active"]
        validators = [
            UniqueTogetherValidator(queryset=User.objects.all(),
                                    fields=["first_name", "last_name"],
                                    message="the couple first_name, last_name should be unique")
        ]

    def validate_role_name(self, value):
        if value in ['ROLE_ADMIN', 'ROLE_SUPER_ADMIN', 'ROLE_PRESIDENT']:
            user = self.context["request"].user
            if not user.role_name in ['ROLE_ADMIN', 'ROLE_SUPER_ADMIN']:
                raise serializers.ValidationError(
                    "Only Admin can perform this action.")
        return value

    def validate(self, data):
        if self.instance:
            user = self.context["request"].user
            if self.instance == user and data["role_name"] and data["role_name"] != self.instance.role_name:
                raise serializers.ValidationError(
                    "You can't change your own role_name.")
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
