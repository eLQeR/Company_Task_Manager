"""
URL configuration for task_manager_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from task_manager.views import (
    ProfileView,
    ProfileDetailView,
    UserUpdateView,
    PasswordChangeViewCustom
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("task_manager.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", ProfileView.as_view(), name="my-profile"),
    path(
        "profile/update-password/",
        PasswordChangeViewCustom.as_view(),
        name="update-password"
    ),
    path(
        "profile/<int:pk>/",
        ProfileDetailView.as_view(),
        name="profile"
    ),
    path(
        "profile/<int:pk>/update/",
        UserUpdateView.as_view(),
        name="my-profile-update"
    ),
    path("__debug__/", include("debug_toolbar.urls"))
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)

app_name = "task_manager_system"
