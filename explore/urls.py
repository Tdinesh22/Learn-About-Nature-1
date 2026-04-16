from django.contrib.auth import views as auth_views
from django.urls import path

from .forms import StyledAuthenticationForm
from .views import SignUpView, ai_helper, entry, home, resources_page, species_detail, species_list, species_view


urlpatterns = [
    path("", entry, name="entry"),
    path("home/", home, name="home"),
    path("ai-helper/", ai_helper, name="ai_helper"),
    path("resources/", resources_page, name="resources"),
    path("species/", species_view, name="species"),
    path("species/list/", species_list, name="species_list"),
    path("species/<int:taxon_id>/", species_detail, name="species_detail"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=StyledAuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
