"""stuco_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from stuco_app import views as home_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

django_login_path = path("django_login/", home_views.django_login, name="login")

login_path = django_login_path

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url="/static/assets/img/favicon.png")),
    path("admin/", admin.site.urls),
    path("accounts/user/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    login_path,
    path("about/", home_views.about, name="about"),
    path("files/", include("file_uploads.urls")),
    path("polls/", include("polls.urls")),
    path("", home_views.home, name="home"),
]

if settings.ENVIRONMENT == "local":
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "StuCo App Administration"
