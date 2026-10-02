from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import HistorialCambio, Ticket


@receiver(pre_save, sender=Ticket)
def ticket_pre_save(sender, instance, **kwargs):
    """
    Obtiene los valores anteriores antes de guardar un Ticket.
    """

    instance._history_changes = []

    if not instance.pk:
        return

    try:
        previous = (
            Ticket.objects
            .select_related("assigned_agent")
            .get(pk=instance.pk)
        )
    except Ticket.DoesNotExist:
        return

    if previous.status != instance.status:
        instance._history_changes.append(
            {
                "field_name": "status",
                "old_value": previous.status,
                "new_value": instance.status,
            }
        )

    if previous.assigned_agent_id != instance.assigned_agent_id:
        instance._history_changes.append(
            {
                "field_name": "assigned_agent",
                "old_value": (
                    str(previous.assigned_agent_id)
                    if previous.assigned_agent_id
                    else None
                ),
                "new_value": (
                    str(instance.assigned_agent_id)
                    if instance.assigned_agent_id
                    else None
                ),
            }
        )


@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    """
    Crea registros de historial después de guardar el Ticket.
    """

    if created:
        return

    changes = getattr(
        instance,
        "_history_changes",
        [],
    )

    modified_by = getattr(
        instance,
        "_modified_by",
        None,
    )

    for change in changes:
        HistorialCambio.objects.create(
            ticket=instance,
            field_name=change["field_name"],
            old_value=change["old_value"],
            new_value=change["new_value"],
            modified_by=modified_by,
        )