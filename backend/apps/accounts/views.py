from rest_framework import serializers
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import UserSerializer
from apps.accounts.models import User, UserRole
from apps.organisations.models import Organisation


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    organisation_name = serializers.CharField(required=False, allow_blank=True)


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = SignupRequestSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        email: str = payload.validated_data["email"].lower().strip()
        password: str = payload.validated_data["password"]
        org_name: str = (payload.validated_data.get("organisation_name") or "").strip()

        if User.objects.filter(email=email).exists():
            return Response({"detail": "Email already in use"}, status=400)

        if not org_name:
            # Friendly default for demo/local: one org per signup.
            org_name = f"{email.split('@')[0]}'s Organisation"

        org = Organisation.objects.create(name=org_name)

        username = email.split("@")[0][:150]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            organisation=org,
            role=UserRole.RESPONDENT,
        )

        # Return the same shape as login: tokens + user.
        token = LoginSerializer.get_token(user)
        return Response(
            {
                "refresh": str(token),
                "access": str(token.access_token),
                "user": UserSerializer(user).data,
            },
            status=201,
        )
