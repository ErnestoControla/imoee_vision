# config/api_router.py

from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from asistente.users.api.views import (
    UserViewSet,
    UserRegistrationView,
    UserProfileView,
)
from core.api.views import RolViewSet

# Seleccionamos DefaultRouter en DEBUG para endpoint raiz y SimpleRouter en producción
router = DefaultRouter() if settings.DEBUG else SimpleRouter()

# Registramos los ViewSets
router.register(r"users", UserViewSet)
router.register(r"roles", RolViewSet, basename="role")

app_name = "api"
urlpatterns = [
    # Endpoints de autenticación y perfil
    path("users/register/", UserRegistrationView.as_view(), name="users-register"),  # POST /api/users/register/
    path("users/me/",       UserProfileView.as_view(),    name="users-me"),        # GET  /api/users/me/

    # Endpoints CRUD para Users y Roles
    *router.urls,
]
