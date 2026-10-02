from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.views import APIView

from .models import Ticket, Comentario, HistorialCambio
from .serializers import (
    TicketSerializer,
    TicketAgentAssignmentSerializer,
    TicketStatusSerializer,
    InternalCommentSerializer,
    HistorialCambioSerializer,
    ComentarioSerializer,
    UserCreateSerializer,
    AgentCreateSerializer,
)
from .permissions import IsAgentOrReadOnlyCustomer, IsAgent, IsSuperUser


class TicketViewSet(viewsets.ModelViewSet):
    """
    Gestión de solicitudes de soporte.

    Clientes:
    - Crear solicitudes.
    - Consultar únicamente sus propias solicitudes.

    Agentes/Admin:
    - Consultar todas las solicitudes.
    - Asignar agentes.
    - Cambiar estados.
    - Agregar comentarios internos.
    - Revisar historial.
    - Eliminar solicitudes.
    """

    serializer_class = TicketSerializer
    permission_classes = [
        IsAuthenticated,
        IsAgentOrReadOnlyCustomer,
    ]

    def get_queryset(self):
        """
        Agentes/Admin:
            pueden ver todos los tickets.

        Clientes:
            solamente pueden ver sus propios tickets.
        """

        queryset = (
            Ticket.objects
            .select_related(
                "customer",
                "assigned_agent",
            )
            .prefetch_related(
                "comments__author",
            )
        )

        user = self.request.user

        if user.is_staff:
            return queryset

        return queryset.filter(
            customer=user
        )

    def perform_create(self, serializer):
        """
        El cliente que crea la solicitud queda automáticamente
        registrado como customer.
        """

        serializer.save()

    def perform_update(self, serializer):
        """
        Las actualizaciones normales quedan reservadas
        a los agentes mediante los permisos del ViewSet.

        Se registra el usuario que realizó el cambio
        para el historial automático.
        """

        serializer.instance._modified_by = self.request.user
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Solo agentes/admin pueden eliminar tickets.
        """

        if not request.user.is_staff:
            return Response(
                {
                    "detail": "Solo los agentes pueden eliminar solicitudes."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)

    # =========================================================
    # ASIGNAR AGENTE
    # =========================================================

    @action(
        detail=True,
        methods=["patch"],
        url_path="assign",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def assign_agent(self, request, pk=None):
        """
        Asigna un agente interno a una solicitud.

        Solo agentes/admin.
        """

        ticket = self.get_object()

        serializer = TicketAgentAssignmentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        agent = serializer.validated_data["agent"]
        
        if ticket.assigned_agent_id == agent.id:
            return Response(
                {"detail": "El agente ya está asignado a esta solicitud."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            ticket._modified_by = request.user
            ticket.assigned_agent = agent
            ticket.save(
                update_fields=[
                    "assigned_agent",
                    "updated_at",
                ]
            )

        return Response(
            TicketSerializer(
                ticket,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # CAMBIAR ESTADO
    # =========================================================

    @action(
        detail=True,
        methods=["patch"],
        url_path="status",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def change_status(self, request, pk=None):
        """
        Cambia el estado de una solicitud.

        Solo agentes/admin.
        """

        ticket = self.get_object()

        serializer = TicketStatusSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        if ticket.status == new_status:
            return Response(
                {
                    "detail": "La solicitud ya tiene ese estado."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            ticket._modified_by = request.user
            ticket.status = new_status
            ticket.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

        return Response(
            TicketSerializer(
                ticket,
                context={"request": request},
            ).data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # COMENTARIO INTERNO
    # =========================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="comments/internal",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def add_internal_comment(self, request, pk=None):
        """
        Agrega un comentario interno a una solicitud.

        Solo agentes/admin.

        El cliente NO puede utilizar este endpoint.
        """

        ticket = self.get_object()

        serializer = InternalCommentSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            ticket=ticket,
            author=request.user,
            is_internal=True,
        )

        return Response(
            ComentarioSerializer(
                comment,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    # =========================================================
    # HISTORIAL
    # =========================================================

    @action(
        detail=True,
        methods=["get"],
        url_path="history",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def history(self, request, pk=None):
        """
        Consulta el historial de cambios de una solicitud.

        Solo agentes/admin.
        """

        ticket = self.get_object()

        history = (
            HistorialCambio.objects
            .filter(ticket=ticket)
            .select_related(
                "modified_by",
                "ticket",
                "ticket__customer",
                "ticket__assigned_agent",
            )
            .order_by("-changed_at")
        )

        serializer = HistorialCambioSerializer(
            history,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    # =========================================================
    # COMENTARIOS
    # =========================================================

    @action(
        detail=True,
        methods=["get"],
        url_path="comments",
        permission_classes=[IsAuthenticated, IsAgent],
    )
    def comments(self, request, pk=None):
        """
        Consulta los comentarios internos de una solicitud.

        Solo agentes/admin.
        """

        ticket = self.get_object()

        comments = (
            Comentario.objects
            .filter(
                ticket=ticket,
                is_internal=True,
            )
            .select_related("author")
            .order_by("created_at")
        )

        serializer = ComentarioSerializer(
            comments,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

class RegisterView(APIView):
    """
    Registro de clientes.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token, created = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Usuario creado correctamente",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_staff": user.is_staff,
                },
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class AgentCreateView(APIView):
    """
    Creación de agentes internos.

    Solo un administrador (superusuario) debería poder
    crear nuevos agentes.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSuperUser]

    def post(self, request):
        serializer = AgentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token, created = Token.objects.get_or_create(
            user=user
        )

        return Response(
            {
                "message": "Agente creado correctamente",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                },
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )