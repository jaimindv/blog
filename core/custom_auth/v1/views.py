from django.contrib.auth import authenticate, login, logout
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from base.permissions import IsAPIKeyAuthenticated
from core.custom_auth.models import User
from core.custom_auth.throttles import FailedLoginThrottle

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    RegisterUserSerializer,
    UserDetailSerializer,
    UserPhotoSerializer,
)


class AppUserViewset(viewsets.ModelViewSet):
    serializer_class = RegisterUserSerializer
    queryset = User.objects.all()
    lookup_field = "pk"

    def get_queryset(self):
        if self.action in ["list", "retrieve", "destroy"]:
            user = self.request.user
            if user.role != "Admin" or not user.is_staff:
                user_id = user.id
                return User.objects.filter(id=user_id)
        return super().get_queryset()

    def get_permissions(self):
        if self.action in ["create", "verify_user"]:
            self.permission_classes = [IsAPIKeyAuthenticated]
        return super().get_permissions()

    def get_authenticators(self):
        request = self.request
        if request.method in ["POST"]:
            self.authentication_classes = []
        return super().get_authenticators()

    def get_serializer_class(self):
        actions = {
            "list": UserDetailSerializer,
            "create": RegisterUserSerializer,
            "update": UserDetailSerializer,
            "partial_update": UserDetailSerializer,
            "retrieve": UserDetailSerializer,
            "change_password": ChangePasswordSerializer,
            "set_profile_photo": UserPhotoSerializer,
        }
        if self.action in actions:
            self.serializer_class = actions.get(self.action)
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if User.objects.filter(email=request.data.get("email")).exists():
            return Response(
                {"message": "A user with that email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = {
            "message": "User regiatered successfully.",
            "data": UserDetailSerializer(user).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_data = {
            "message": "User profile updated successfully.",
            "data": UserDetailSerializer(instance).data,
        }
        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Password updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Password updated successfully.",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid request",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Invalid old password."
                        ),
                    },
                ),
            ),
        },
    )
    @action(methods=["PUT"], detail=False, url_path="change-password")
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response(
            {"message": "Password updated successfully."}, status=status.HTTP_200_OK
        )

    @action(methods=["PUT"], detail=False, url_path="set-profile-photo")
    def set_profile_photo(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            response_data = {
                "message": "Profile pic uploaded successfully.",
                "data": UserDetailSerializer(instance).data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["DELETE"], detail=False, url_path="delete-profile-photo")
    def delete_profile_photo(self, request, *args, **kwargs):
        user = request.user
        user.profile_pic.delete()
        user.save()
        response_data = {
            "message": "Profile pic deleted successfully.",
            "data": UserDetailSerializer(user).data,
        }
        return Response(
            response_data,
            status=status.HTTP_204_NO_CONTENT,
        )


class LoginView(views.APIView):
    authentication_classes = []
    permission_classes = [IsAPIKeyAuthenticated]
    throttle_classes = [FailedLoginThrottle]
    throttle_scope = "failed_login"

    @swagger_auto_schema(
        operation_description="Login API using email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login Successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Login Successful"
                        ),
                        "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, example="user@example.com"
                        ),
                        "role": openapi.Schema(
                            type=openapi.TYPE_STRING, example="admin"
                        ),
                        "refresh_token": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJhbGciOiJIUzI1NiIsIn...",
                        ),
                        "access_token": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="eyJhbGciOiJIUzI1NiIsIn...",
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid email or password",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Invalid email."
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        if not User.objects.filter(email=email).exists():
            return self.failed_attempt(email, "Invalid email.")

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user, backend="core.custom_auth.backends.AppUserAuthBackend")
            refresh_token = RefreshToken.for_user(user)
            response = {
                "message": "Login Successful.",
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token),
            }
            return Response(data=response)
        else:
            return self.failed_attempt(email, "Incorrect password.")

    def failed_attempt(self, email, error_message):
        """Apply throttling only when login fails."""
        throttle = FailedLoginThrottle()
        request = self.request

        if throttle.allow_request(request, self):
            return Response(
                {"error": error_message}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {"error": "Too many failed login attempts. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )


class LogoutView(views.APIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh_token": openapi.Schema(
                    type=openapi.TYPE_STRING, description="JWT Refresh Token"
                )
            },
            required=["refresh_token"],
        ),
        responses={
            200: openapi.Response(
                description="Logout Successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, example="Logout successful."
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Invalid or already Blacklisted Refresh token.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Invalid or already Blacklisted Refresh token.",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            # Blacklist token
            token = RefreshToken(refresh_token)
            token.blacklist()
            logout(request)
            return Response(
                {"message": "Logout successful."}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"error": "Invalid or already Blacklisted Refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
