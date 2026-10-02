from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comentario, HistorialCambio, Ticket


User = get_user_model()


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]


class ComentarioSerializer(serializers.ModelSerializer):
    author = UserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = Comentario
        fields = [
            "id",
            "ticket",
            "author",
            "text",
            "is_internal",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "is_internal",
        ]


class HistorialCambioSerializer(serializers.ModelSerializer):
    modified_by = UserSummarySerializer(
        read_only=True,
    )

    class Meta:
        model = HistorialCambio
        fields = [
            "id",
            "ticket",
            "field_name",
            "old_value",
            "new_value",
            "modified_by",
            "changed_at",
        ]


class TicketSerializer(serializers.ModelSerializer):
    customer = UserSummarySerializer(
        read_only=True,
    )

    assigned_agent = UserSummarySerializer(
        read_only=True,
    )

    comments = ComentarioSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "subject",
            "description",
            "priority",
            "status",
            "customer",
            "assigned_agent",
            "comments",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "customer",
            "assigned_agent",
            "status",
            "comments",
            "created_at",
            "updated_at",
        ]

    def validate_subject(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El asunto no puede estar vacío."
            )

        return value

    def validate_description(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "La descripción no puede estar vacía."
            )

        return value

    def create(self, validated_data):
        request = self.context["request"]

        return Ticket.objects.create(
            customer=request.user,
            **validated_data,
        )


class TicketAgentAssignmentSerializer(serializers.Serializer):
    agent_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(
            is_staff=True,
            is_active=True,
        ),
        source="agent",
    )


class TicketStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Ticket.Status.choices,
    )


class InternalCommentSerializer(serializers.Serializer):
    text = serializers.CharField(
        min_length=1,
        max_length=5000,
        trim_whitespace=True,
    )
    
    def create(self, validated_data):
        return Comentario.objects.create(**validated_data)

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email", ""),
        )

        return user

class AgentCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            email=validated_data.get("email", ""),
        )

        # Convertir el usuario en Agente
        user.is_staff = True
        user.is_superuser = False
        user.save(update_fields=["is_staff", "is_superuser"])

        return user