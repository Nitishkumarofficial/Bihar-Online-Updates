"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from django.views.generic import TemplateView

from newsportal.admin import admin_site
from newsportal import views

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', views.home, name='home'),
    path(
        'updates/<int:pk>/<slug:slug>/',
        views.update_detail,
        name='update-detail',
    ),
    path(
        'updates/updates-1.html',
        TemplateView.as_view(
            template_name='newsportal/legacy/updates-1.html'
        ),
        name='legacy-update-1',
    ),
    path(
        'updates/updates-2.html',
        views.legacy_job_update,
        name='legacy-update-2',
    ),
    path(
        'updates/updates-3.html',
        TemplateView.as_view(
            template_name='newsportal/legacy/updates-3.html'
        ),
        name='legacy-update-3',
    ),
    path(
        'view all updates/all-updates.html',
        views.all_updates,
        name='legacy-all-updates',
    ),
    path(
        'information/<slug:section>/',
        views.site_info,
        name='site-info',
    ),
]
