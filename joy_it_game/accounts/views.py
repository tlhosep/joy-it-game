""" module: views
** Content **
This module provides the registration functioality 

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'register.html'