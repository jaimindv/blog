from rest_framework import serializers

from .models import User


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "bio",
            "role",
        ]
        extra_kwargs = {"password": {"required": True, "write_only": True}}

    def create(self, validated_data):
        password = validated_data.get("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "bio",
            "role",
            "profile_pic",
        ]
        read_only_fields = ["profile_pic"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        if old_password == new_password:
            raise serializers.ValidationError(
                {"message": "New password cannot be same as old password."}
            )

        request = self.context.get("request")
        user = request.user
        if not user.check_password(old_password):
            raise serializers.ValidationError({"message": "Incorrect old password."})
        return attrs


class UserPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "profile_pic"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
