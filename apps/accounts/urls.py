"""
Accounts URL Configuration
Authentication and user management URLs.
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import (
    CustomPasswordChangeForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
)

app_name = "accounts"

urlpatterns = [
    # Authentication
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="accounts/logged_out.html"
        ),
        name="logout"
    ),
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register"
    ),
    
    # Profile Management
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile"
    ),
    path(
        "profile/edit/",
        views.ProfileEditView.as_view(),
        name="profile_edit"
    ),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html",
            form_class=CustomPasswordChangeForm,
            success_url="/accounts/password/change/done/",
        ),
        name="password_change"
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done"
    ),
    
    # Password Reset
    path(
        "password/reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            form_class=CustomPasswordResetForm,
            email_template_name="accounts/emails/password_reset_email.html",
            subject_template_name="accounts/emails/password_reset_subject.txt",
            success_url="/accounts/password/reset/done/",
        ),
        name="password_reset"
    ),
    path(
        "password/reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done"
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            form_class=CustomSetPasswordForm,
            success_url="/accounts/password/reset/complete/",
        ),
        name="password_reset_confirm"
    ),
    path(
        "password/reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete"
    ),
    
    # Address Management
    path(
        "addresses/",
        views.AddressListView.as_view(),
        name="address_list"
    ),
    path(
        "addresses/add/",
        views.AddressCreateView.as_view(),
        name="address_add"
    ),
    path(
        "addresses/<int:pk>/edit/",
        views.AddressUpdateView.as_view(),
        name="address_edit"
    ),
    path(
        "addresses/<int:pk>/delete/",
        views.AddressDeleteView.as_view(),
        name="address_delete"
    ),
    path(
        "addresses/<int:pk>/set-default/",
        views.AddressSetDefaultView.as_view(),
        name="address_set_default"
    ),
    
    # Order History
    path(
        "orders/",
        views.OrderHistoryView.as_view(),
        name="order_history"
    ),
]
