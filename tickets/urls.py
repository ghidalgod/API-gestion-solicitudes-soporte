from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet,  RegisterView, AgentCreateView

router = DefaultRouter()

router.register(
    "tickets",
    TicketViewSet,
    basename="ticket",
)


urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),
    path("agents/", AgentCreateView.as_view(), name="create-agent"),
]

