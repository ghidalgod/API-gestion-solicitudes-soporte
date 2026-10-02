from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import HistorialCambio, Ticket


User = get_user_model()


class TicketAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="StrongPassword123!",
        )

        self.agent = User.objects.create_user(
            username="agent",
            email="agent@example.com",
            password="StrongPassword123!",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.customer,
        )

    def test_create_ticket(self):
        response = self.client.post(
            "/api/tickets/",
            {
                "subject": "Problema con el login",
                "description": (
                    "El usuario no puede iniciar sesión."
                ),
                "priority": "HIGH",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        ticket = Ticket.objects.get()

        self.assertEqual(
            ticket.subject,
            "Problema con el login",
        )

        self.assertEqual(
            ticket.customer,
            self.customer,
        )

        self.assertEqual(
            ticket.priority,
            Ticket.Priority.HIGH,
        )

        self.assertEqual(
            ticket.status,
            Ticket.Status.OPEN,
        )

    def test_agent_can_change_ticket_status(self):
        ticket = Ticket.objects.create(
            subject="Error API",
            description="La API devuelve 500.",
            priority=Ticket.Priority.MEDIUM,
            customer=self.customer,
        )

        self.client.force_authenticate(
            user=self.agent,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/status/",
            {
                "status": Ticket.Status.IN_PROGRESS,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        ticket.refresh_from_db()

        self.assertEqual(
            ticket.status,
            Ticket.Status.IN_PROGRESS,
        )

    def test_status_change_creates_history(self):
        ticket = Ticket.objects.create(
            subject="Problema de conexión",
            description="No hay conexión.",
            priority=Ticket.Priority.HIGH,
            customer=self.customer,
        )

        self.client.force_authenticate(
            user=self.agent,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/status/",
            {
                "status": Ticket.Status.RESOLVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        history = HistorialCambio.objects.filter(
            ticket=ticket,
            field_name="status",
        )

        self.assertEqual(
            history.count(),
            1,
        )

        change = history.first()

        self.assertEqual(
            change.old_value,
            Ticket.Status.OPEN,
        )

        self.assertEqual(
            change.new_value,
            Ticket.Status.RESOLVED,
        )

        self.assertEqual(
            change.modified_by,
            self.agent,
        )

    def test_agent_assignment_creates_history(self):
        ticket = Ticket.objects.create(
            subject="Error de permisos",
            description="Usuario sin permisos.",
            priority=Ticket.Priority.MEDIUM,
            customer=self.customer,
        )

        self.client.force_authenticate(
            user=self.agent,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/assign/",
            {
                "agent_id": self.agent.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        history = HistorialCambio.objects.filter(
            ticket=ticket,
            field_name="assigned_agent",
        )

        self.assertEqual(
            history.count(),
            1,
        )

        change = history.first()

        self.assertIsNone(
            change.old_value,
        )

        self.assertEqual(
            change.new_value,
            str(self.agent.id),
        )

        self.assertEqual(
            change.modified_by,
            self.agent,
        )

    def test_customer_cannot_change_status(self):
        ticket = Ticket.objects.create(
            subject="Solicitud",
            description="Descripción",
            priority=Ticket.Priority.LOW,
            customer=self.customer,
        )

        response = self.client.patch(
            f"/api/tickets/{ticket.id}/status/",
            {
                "status": Ticket.Status.RESOLVED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        ticket.refresh_from_db()

        self.assertEqual(
            ticket.status,
            Ticket.Status.OPEN,
        )

    def test_internal_comment(self):
        ticket = Ticket.objects.create(
            subject="Problema",
            description="Descripción",
            priority=Ticket.Priority.MEDIUM,
            customer=self.customer,
        )

        self.client.force_authenticate(
            user=self.agent,
        )

        response = self.client.post(
            f"/api/tickets/{ticket.id}/comments/internal/",
            {
                "text": "Comentario interno del agente.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
        )

        self.assertEqual(
            ticket.comments.count(),
            1,
        )

        comment = ticket.comments.first()

        self.assertEqual(
            comment.author,
            self.agent,
        )

        self.assertTrue(
            comment.is_internal,
        )