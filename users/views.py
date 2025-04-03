from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserStatusUpdateSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(password):
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "Account is deactivated"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                    "is_active": user.is_active,
                },
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Only Admin can see all users, Manager can see regular users
        if request.user.role == "ADMIN":
            users = User.objects.all()
        elif request.user.role == "MANAGER":
            users = User.objects.filter(role="USER")
        else:
            return Response(
                {"error": "Not authorized to view users"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Only Admin can create any type of user, Manager can create regular users
        if request.user.role == "ADMIN":
            serializer = UserSerializer(data=request.data)
        elif request.user.role == "MANAGER" and request.data.get("role") == "USER":
            serializer = UserSerializer(data=request.data)
        else:
            return Response(
                {"error": "Not authorized to create this type of user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            # Admin can access any user, Manager can access only regular users, Users can access only themselves
            if self.request.user.role == "ADMIN":
                return user
            elif self.request.user.role == "MANAGER" and user.role == "USER":
                return user
            elif self.request.user.id == user.id:
                return user
            return None
        except User.DoesNotExist:
            return None

    def get(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response(
                {"error": "User not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response(
                {"error": "User not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only Admin can change roles, others can update other fields
        if (
            request.user.role != "ADMIN"
            and "role" in request.data
            and request.data["role"] != user.role
        ):
            return Response(
                {"error": "You cannot change user roles"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        user = self.get_object(user_id)
        if not user:
            return Response(
                {"error": "User not found or not authorized"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only Admin can delete users
        if request.user.role != "ADMIN":
            return Response(
                {"error": "Only Admin can delete users"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserActivationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        # Only Admin and Manager can activate/deactivate users
        if request.user.role not in ["ADMIN", "MANAGER"]:
            return Response(
                {"error": "Not authorized to change user status"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)

            # Manager can only activate/deactivate regular users
            if request.user.role == "MANAGER" and user.role != "USER":
                return Response(
                    {"error": "Managers can only modify regular user status"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = UserStatusUpdateSerializer(
                user, data=request.data, partial=True
            )

            if serializer.is_valid():
                # Reset failed tasks count if reactivating
                if "is_active" in request.data and request.data["is_active"] is True:
                    serializer.validated_data["failed_tasks"] = 0

                serializer.save()
                return Response(serializer.data)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
