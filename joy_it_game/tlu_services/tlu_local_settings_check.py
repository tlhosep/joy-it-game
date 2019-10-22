""" module: tlu_local_settings

** Content **
Checks the mail connectivity

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-24 
"""

from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.mail.message import EmailMessage
    
def checkMailOk(self, subject='Testmail', message='Testmessage', from_email='test@test.de', to_mail='to@test.de') -> bool:
    """
    Check if the configured mail functionality works as desired
    :param subject: subject of test-email
    :param message: message for test-email
    :param from_email: sender
    :param to_mail: receiver
    """
    email = EmailMessage(
        subject,
        message,
        from_email,
        [to_mail],
        )
    
    if email.send(fail_silently=True) > 0:
        return True
    return False
    
class settingsCheckForm(forms.Form):
    emailSubject=forms.CharField(label=_("Subject"), initial=_("Testmail"), required=True)
    emailMessage=forms.CharField(widget=forms.Textarea(attrs={"rows":3,"cols":40}),label=_("Some Text"), initial=_("This is a simple testmail."), required=True)
    emailFrom=forms.EmailField(label=_("From(email)"), initial=_("me@test.com"), required=True)
    emailTo=forms.EmailField(label=_("To(email)"), initial=_("me@test.com"), required=True)
    emailSuccess=forms.BooleanField(label=_("Email check passed without issues?"), initial=False, required=False)
