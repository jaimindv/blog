from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from base.permissions import IsAPIKeyAuthenticated

from .models import User
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

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        if not User.objects.filter(email=email).exists():
            return Response(
                {
                    "error": "Invalid email.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user, backend="core.custom_auth.backends.AppUserAuthBackend")
            # JWT token
            refresh_token = RefreshToken.for_user(user)
            response = {
                "message": "Login Successfully",
                "user_id": user.id,
                "email": user.email,
                "role": user.role,
                "refresh_token": str(refresh_token),
                "access_token": str(refresh_token.access_token),
            }
            return Response(data=response)
        else:
            return Response(
                {
                    "error": "Incorrect password.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutView(views.APIView):

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
