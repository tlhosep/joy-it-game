""" module: setup_adminuser
** Content **
This app is used during the deployment process to make sure that we do have at least one admin in the database

** Details **
See https://stackoverflow.com/questions/39744593/how-to-create-a-django-superuser-if-it-doesnt-exist-non-interactively

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-23 
""" 

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    """
    Commandline interface to check and add an admin, if not already existing
    """
    help = "Creates an admin user non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        parser.add_argument('--username', help=_("Admin's username"), required=True)
        parser.add_argument('--email', help=_("Admin's email"), required=True)
        parser.add_argument('--password', help=_("Admin's password"), required=True)
        parser.add_argument('--language', help=_("The to be used language"), required=False)

    def handle(self, *args, **options):
        """
        Main loop to process the commandline
        """
        User = get_user_model()
        if not User.objects.filter(username=options['username']).exists():
            User.objects.create_superuser(username=options['username'],
                                          email=options['email'],
                                          password=options['password'])