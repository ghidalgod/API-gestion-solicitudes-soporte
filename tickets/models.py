from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


User = get_user_model()


class Ticket(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        MEDIUM = "MEDIUM", "Media"
        HIGH = "HIGH", "Alta"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Abierto"
        IN_PROGRESS = "IN_PROGRESS", "En Progreso"
        RESOLVED = "RESOLVED", "Resuelto"

    subject = models.CharField(
        "Asunto",
        max_length=255,
    )

    description = models.TextField(
    "Descripción",
    )

    priority = models.CharField(
    "Prioridad",
    max_length=20,
    choices=Priority.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    customer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="customer_tickets",
    )

    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="assigned_tickets",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status"],
                name="ticket_status_idx",
            ),
            models.Index(
                fields=["priority"],
                name="ticket_priority_idx",
            ),
            models.Index(
                fields=["assigned_agent"],
                name="ticket_agent_idx",
            ),
            models.Index(
                fields=["customer"],
                name="ticket_customer_idx",
            ),
            models.Index(
                fields=["created_at"],
                name="ticket_created_idx",
            ),
        ]

    def __str__(self):
        return f"#{self.pk} - {self.subject}"

    def clean(self):
        if (
            self.assigned_agent_id
            and self.assigned_agent_id == self.customer_id
        ):
            raise ValidationError(
                {
                    "assigned_agent": (
                        "El cliente no puede ser asignado "
                        "como agente del mismo ticket."
                    )
                }
            )


class Comentario(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ticket_comments",
    )

    text = models.TextField()

    is_internal = models.BooleanField(
        "Comentario interno",
        default=True,
    )

    created_at = models.DateTimeField(
        "Fecha de creación",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=["ticket", "created_at"],
                name="comment_ticket_date_idx",
            ),
        ]

    def __str__(self):
        return f"Comentario #{self.pk} - Ticket #{self.ticket_id}"


class HistorialCambio(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="change_history",
    )

    field_name = models.CharField(
        max_length=100,
    )

    old_value = models.TextField(
        null=True,
        blank=True,
    )

    new_value = models.TextField(
        null=True,
        blank=True,
    )

    modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="ticket_changes",
        null=True,
        blank=True,
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-changed_at"]
        indexes = [
            models.Index(
                fields=["ticket", "changed_at"],
                name="history_ticket_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.field_name}: "
            f"{self.old_value} -> {self.new_value}"
        )