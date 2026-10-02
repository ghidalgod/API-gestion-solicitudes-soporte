from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import TokenProxy


from .models import Comentario, HistorialCambio, Ticket

# =========================
# USUARIOS
# =========================

admin.site.unregister(User)
admin.site.unregister(TokenProxy)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "id",
        "username",
        "first_name",
        "last_name",
        "email",
        "user_type",
        "is_active",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )

    @admin.display(description="Tipo")
    def user_type(self, obj):
        if obj.is_superuser:
            return "Administrador"
        if obj.is_staff:
            return "Agente"
        return "Cliente"

@admin.register(TokenProxy)
class CustomTokenAdmin(admin.ModelAdmin):
    list_display = (
        "key_masked",
        "user",
    )

    @admin.display(description="Token")
    def key_masked(self, obj):
        return "••••••••••••••••••••••••"

    search_fields = (
        "user__username",
        "user__email",
    )
# =========================
# TICKETS
# =========================

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "subject",
        "priority",
        "status",
        "customer",
        "assigned_agent",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "assigned_agent",
    )

    search_fields = (
        "subject",
        "description",
        "customer__username",
        "assigned_agent__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

# =========================
# COMENTARIOS
# =========================

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "author",
        "is_internal",
        "created_at",
    )

    list_filter = (
        "is_internal",
    )

    search_fields = (
        "text",
        "author__username",
    )

# =========================
# HISTORIAL
# =========================

@admin.register(HistorialCambio)
class HistorialCambioAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "ticket_subject",
        "customer_name",
        "assigned_agent_info",
        "field_name_display",
        "old_value_display",
        "new_value_display",
        "modified_by",
        "changed_at",
    )

    list_filter = (
        "field_name",
        "changed_at",
    )

    search_fields = (
        "ticket__subject",
        "ticket__customer__username",
        "ticket__customer__first_name",
        "ticket__customer__last_name",
        "ticket__assigned_agent__username",
        "modified_by__username",
    )

    ordering = (
        "ticket_id",
        "changed_at",
    )

    @admin.display(description="Ticket", ordering="ticket_id")
    def ticket_id(self, obj):
        return f"Ticket #{obj.ticket_id}"

    @admin.display(description="Asunto")
    def ticket_subject(self, obj):
        return obj.ticket.subject

    @admin.display(description="Cliente")
    def customer_name(self, obj):
        customer = obj.ticket.customer

        full_name = f"{customer.first_name} {customer.last_name}".strip()

        if full_name:
            return full_name

        return customer.username

    @admin.display(description="Agente asignado")
    def assigned_agent_info(self, obj):
        agent = obj.ticket.assigned_agent

        if not agent:
            return "Sin agente"

        full_name = f"{agent.first_name} {agent.last_name}".strip()

        if full_name:
            return f"#{agent.id} - {full_name}"

        return f"#{agent.id} - {agent.username}"

    @admin.display(description="Campo modificado")
    def field_name_display(self, obj):
        campos = {
            "status": "Estado",
            "assigned_agent": "Agente asignado",
        }

        return campos.get(obj.field_name, obj.field_name)

    @admin.display(description="Valor anterior")
    def old_value_display(self, obj):
        return obj.old_value or "Sin valor"

    @admin.display(description="Valor nuevo")
    def new_value_display(self, obj):
        return obj.new_value or "Sin valor"
    