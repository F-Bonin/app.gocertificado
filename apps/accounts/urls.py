from django.urls import path
from .views import (
    UserRegistrationView, CustomLoginView, CustomLogoutView,
    ChangeFirstPasswordView, TeamListView, TeamCreateView,
    TeamUpdateView, TeamDeleteView, TeamSendInviteEmailView
)

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("primeiro-acesso/", ChangeFirstPasswordView.as_view(), name="change_password"),

    # Gestão de Equipe (Minha Equipe)
    path("equipe/", TeamListView.as_view(), name="team_list"),
    path("equipe/novo/", TeamCreateView.as_view(), name="team_create"),
    path("equipe/<int:pk>/editar/", TeamUpdateView.as_view(), name="team_update"),
    path("equipe/<int:pk>/excluir/", TeamDeleteView.as_view(), name="team_delete"),
    path("equipe/<int:pk>/enviar-convite/", TeamSendInviteEmailView.as_view(), name="team_send_invite"),
]
