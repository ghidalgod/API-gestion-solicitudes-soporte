from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )
    
class IsAgentOrReadOnlyCustomer(BasePermission):
    """
    Agentes/staff pueden gestionar tickets.
    Clientes pueden trabajar únicamente con sus propios tickets.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_staff:
            return True

        return obj.customer_id == user.id


class IsAgent(BasePermission):
    """
    Permite operaciones exclusivas para agentes/staff.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )