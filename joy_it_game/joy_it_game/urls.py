"""joy_it_game URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')), #for internationalization
    path('tlu_joyit_game/', include('tlu_joyit_game.urls')), #the main-application
    path('admin/', admin.site.urls), #given administartion site
    path('admin/docs/', include('django.contrib.admindocs.urls')), #documentation
    path('accounts/', include('accounts.urls')), #user handling
    path('accounts/', include('django.contrib.auth.urls')), #login handling
]
