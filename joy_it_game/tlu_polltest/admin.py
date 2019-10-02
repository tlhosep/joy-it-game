""" module: admin
** Content **
Leftover from very first implementation 

** Details **
* To be removed *

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 
from django.contrib import admin
# Register your models here.
from .models import Question, Choice

admin.site.register(Question)
admin.site.register(Choice)