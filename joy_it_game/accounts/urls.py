""" module: urls
** Content **
This module adds the accounts/register url 

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-12 
""" 

from django.urls import path

from . import views


urlpatterns = [
    path('register/', views.SignUp.as_view(), name='register'),
]