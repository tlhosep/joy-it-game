""" module: setup_settings
** Content **
This app is used during the deployment process to help to setup the local settings file properly.

** Details **
This is needed as the settings should *NOT* be changed at runtime

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-23 
""" 

from django.core.management.base import BaseCommand
from tlu_services.tlu_local_settings import local_settings
from PyInquirer import style_from_dict, Token, prompt, Validator, ValidationError
import logging
from django.utils.translation import gettext_lazy as _
import os
from tlu_services.tlu_local_settings_check import checkMailOk
import smtplib
import re
import sys
from django.utils import translation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Commandline interface to setup or change the local_settings
    """
    help = "Creates local_settings.py"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = style_from_dict({
            Token.Separator: '#cc5454',
            Token.QuestionMark: '#673ab7 bold',
            Token.Selected: '#cc5454',  # default
            Token.Pointer: '#673ab7 bold',
            Token.Instruction: '',  # default
            Token.Answer: '#f44336 bold',
            Token.Question: '',
        })
    
    def add_arguments(self, parser):
        parser.add_argument('--email_backend', help=_("Email-backend module name"), required=False)
        parser.add_argument('--email_host', help=_("email-hostname/url"), required=False)
        parser.add_argument('--email_host_user', help=_("Emailserver's username"), required=False)
        parser.add_argument('--email_host_password', help=_("Emailserver's password"), required=False)
        parser.add_argument('--email_port', help=_("Emailserver's port"), required=False)
        parser.add_argument('--email_use_tls', help=_("Emailserver should use TLS"), required=False)
        parser.add_argument('--email_file_path', help=_("In case for filesystem option: path"), required=False)
        parser.add_argument('--log_level', help=_("Log-Level for the application"), required=False)
        parser.add_argument('--editsettings', help=_("Do change the settings file"), required=False)
        parser.add_argument('--language', help=_("The to be used language"), required=False)

    class NumberValidator(Validator):
        def validate(self, document):
            try:
                int(document.text)
            except ValueError:
                raise ValidationError(
                    message=_('Please enter a number'),
                    cursor_position=len(document.text))  # Move cursor to end
                
    class FilePathValidator(Validator):
        def validate(self, value):
            if len(value.text):
                if os.path.exists(value.text):
                    return True
                else:
                    raise ValidationError(
                        message=_("Path not found"),
                        cursor_position=len(value.text))
            else:
                raise ValidationError(
                    message=_("You can't leave this blank"),
                    cursor_position=len(value.text))

    class EmailValidator(Validator):
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
    
        def validate(self, email):
            if len(email.text):
                if re.match(self.pattern, email.text):
                    return True
                else:
                    raise ValidationError(
                        message=_("Invalid email"),
                        cursor_position=len(email.text))
            else:
                raise ValidationError(
                    message=_("You can't leave this blank"),
                    cursor_position=len(email.text))

    def genQuestion(self,settings,item_name, message, **kwargs):
        password=False
        confirmation=False
        number=False
        filepath=False
        for key,value in kwargs.items():
            if key=='password':
                password=value
            elif key == 'confirmation':
                confirmation=value
            elif key == 'number':
                number=value
            elif key == 'filepath':
                filepath=value
        questions=[]
        default=str(settings.SETTINGS[item_name])
        input_type = 'input'
        if password==True:
            input_type = 'password'
        elif confirmation == True:
            input_type = 'confirm'
        dictionary={
            'type': input_type,
            'name': item_name,
            'message': message,
            'default' : default,
            }
        if number == True:
            numdict={
                'validate': self.NumberValidator,
                'filter': lambda val: int(val),
            }
            dictionary.update(numdict)
        elif filepath == True:
            filedict={
                'validate': self.FilePathValidator,
            }
            dictionary.update(filedict)
            
        questions.append(dictionary)
        answers = prompt(questions, style=self.style)
        if number == True:
            settings.SETTINGS[item_name]=int(answers[item_name])
        elif confirmation == True:
            settings.SETTINGS[item_name]=bool(answers[item_name])
        else:
            settings.SETTINGS[item_name]=answers[item_name]
        
    def genQuestionList(self,settings,item_name, message, choices):
        questions=[]
        default=settings.SETTINGS[item_name]
        input_type = 'expand'
        choicelist=[]
        i=0
        default_pos=0
        for value,name in choices:
            d = {
                    'key': str(i),
                    'name':name,
                    'value':value,
            }
            choicelist.append(d)
            if value==default:
                default_pos=i
            i += 1
        dictionary={
            'type': input_type,
            'name': item_name,
            'message': message,
            'default' : default_pos,  #currently not working due to a bug, might be solved later on: https://github.com/CITGuru/PyInquirer/issues/67
            'choices' : choicelist,
            }
        questions.append(dictionary)
        answers = prompt(questions, style=self.style)
        settings.SETTINGS[item_name]=answers[item_name]
 
    def genSimpleQuestion(self,item_name, default, message, **kwargs):
        confirmation=False
        emailvalidation=False
        for key,value in kwargs.items():
            if key=='emailvalidation':
                emailvalidation=value
            elif key == 'confirmation':
                confirmation=value
        questions=[]
        input_type = 'input'
        if confirmation == True:
            input_type = 'confirm'
        dictionary={
            'type': input_type,
            'name': item_name,
            'message': message,
            'default' : default,
            }
        if emailvalidation == True:
            numdict={
                'validate': self.EmailValidator,
            }
            dictionary.update(numdict)
            
        questions.append(dictionary)
        answers = prompt(questions, style=self.style)
        return answers[item_name]
      
        
    def handle(self, *args, **options):
        """
        Main loop to process the commandline
        Logic:
        - if file exists:
            - Perform check and return result (0/1) as string
        - else:
            - Ask parameter and save/create file
            - return 1 as string
        The shell calls this commandline as often as needed until it returns with "0"
        """
        language=options["language"]
        if (language != None) and (len(language)>1):
            translation.activate(language)
        settings = local_settings()
        settings.setValuesFromOptions(**options) #use all given commandline-parameter
        editsettings=options["editsettings"]
        if settings.presence() and ((editsettings == None) or (len(editsettings) < 1)):
            settings.read()
            print(_("Settings now loaded, next we check for the email-functionality"))
            backend=settings.SETTINGS['EMAIL_BACKEND']
            email_subject=str(_("Testmail"))
            email_from=str(_("me@me.com"))
            email_to=str(_("me@me.com"))
            email_message=str(_("This is a testmail from the Joy-it-game"))
            
            if backend == 'django.core.mail.backends.smtp.EmailBackend':
                #only ask for subject, sender and receiver for real emails
                email_subject=self.genSimpleQuestion("Subject", email_subject, _("Please enter the subject for your testmail"))
                email_from=self.genSimpleQuestion("From", email_from, _("Please enter the sender"),mailvalidation=True)
                email_to=self.genSimpleQuestion("From", email_to, _("Please enter the receiver"),mailvalidation=True)
                
            email_error=False
            try:
                if checkMailOk(email_subject,email_message,email_from,email_to):
                    email_error=False
                    email_message = _("The Mail has been successfully transmitted! Please check your inbox or the chosen medium.")
                else:
                    email_error=True
                    email_message = _("The Mail could not be delivered!")
            except smtplib.SMTPException as e:
                email_error=True
                email_message = _("We faced the following problem: ")+str(e)
            except BaseException as e:
                email_error=True
                email_message = _("We have encountered an unknown error during trying to submit the test-message: ")+ str(e)
    
            print(email_message)
            if email_error:
                no_issue=self.genSimpleQuestion("no_issue", False, _("Continue anyhow?"), confirmation=True)
                if no_issue:
                    sys.stderr.write("0")
                else:
                    sys.stderr.write("1")
                return
                
            no_issue=self.genSimpleQuestion("no_issue", True, _("Email delivered?"), confirmation=True)
            if no_issue:
                sys.stderr.write("0")
            else:
                sys.stderr.write("1")
            return
        
        if settings.presence():
            settings.read()
            
 
        emailbackendlist= (
            ('django.core.mail.backends.console.EmailBackend',_('Use console')),
            ('django.core.mail.backends.smtp.EmailBackend',_('via Email-Server')),
            ('django.core.mail.backends.filebased.EmailBackend', _('store in filesystem'))
            )
        self.genQuestionList(settings, "EMAIL_BACKEND", _('Please select the email-backend to use'), emailbackendlist)
        backend=settings.SETTINGS['EMAIL_BACKEND']
        if backend == 'django.core.mail.backends.smtp.EmailBackend':
            self.genQuestion(settings, "EMAIL_HOST", _("Please enter the email-server url"))
            self.genQuestion(settings, "EMAIL_HOST_USER", _("Please enter the email-server username"))
            self.genQuestion(settings, "EMAIL_HOST_PASSWORD", _("Please enter the email-server password for the user"),password=True)
            self.genQuestion(settings, "EMAIL_PORT", _("Please enter the email-server port"),number=True)
            self.genQuestion(settings,'EMAIL_USE_TLS', _('Shall we use TLS?'), confirmation=True)
        elif backend == 'django.core.mail.backends.filebased.EmailBackend':
            self.genQuestion(settings,'EMAIL_FILE_PATH',_("Where should the email-file be placed?"),filepath=True)
            
        loglevellist = (
        (logging.FATAL,_('Fatal errors only')),
        (logging.CRITICAL,_('Critical errors only')),
        (logging.ERROR,_('All errors')),
        (logging.DEBUG,_('Debug infos')),
        (logging.INFO,_('Details')),
        )
        self.genQuestionList(settings, "LOG_LEVEL", _("Please select the correct log-level"), loglevellist)
        settings.save() #persist the new settings
        sys.stderr.write("1")
        
