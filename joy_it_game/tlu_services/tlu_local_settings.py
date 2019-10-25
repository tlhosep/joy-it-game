""" module: tlu_local_settings

** Content **
This module shall set, modify and check the presence of a local settings file

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-22 
"""

import os
from builtins import str
from django import forms
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

    
class local_settings():
    """
    Class to set, modify and check the presence of a local settings file
    """
    SITE_ROOT = "" #root of application
    SETTINGS_PATH="" #path of settings-file
    LOCAL_SETTINGS_File="" # local settings file with individual settings
    lsfile=None
    SETTINGS = None
    MYBASE_DIR = ""
    
    def __init__(self):
        self.MYBASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.setDefaults()
        self.SITE_ROOT = os.path.dirname(os.path.realpath(self.MYBASE_DIR)) #for below :)    
        self.SETTINGS_PATH = os.path.join(self.SITE_ROOT, 'joy_it_game')   #path for settings
        self.LOCAL_SETTINGS_File = os.path.join(self.SETTINGS_PATH, 'local_settings.py')
        logging.debug("Site-RooT="+self.SITE_ROOT+" settings="+self.SETTINGS_PATH)

    def setDefaults(self):
        self.SETTINGS = {
            'EMAIL_BACKEND' : 'django.core.mail.backends.console.EmailBackend',
            'EMAIL_HOST' : '127.0.0.1',
            'EMAIL_HOST_USER' : '',
            'EMAIL_HOST_PASSWORD' : '',
            'EMAIL_PORT' : 587,
            'EMAIL_USE_TLS' : True,
            'EMAIL_FILE_PATH' : os.path.dirname(os.path.realpath(self.MYBASE_DIR)),
            'LOG_LEVEL' : logging.ERROR 
            }
     
# See settingsForm class below as well, if you make changes here! 
    def setValues(self, parmdict):
        """
        setup the SETTINGS dictionary from the values given by the parameterdict
        :param parmdict: settings returned from form
        """
        backend=parmdict.get('emailBackend')
        self.SETTINGS['EMAIL_BACKEND']=backend
        if backend == 'django.core.mail.backends.smtp.EmailBackend':
            self.SETTINGS['EMAIL_HOST']=parmdict.get('emailHost')
            self.SETTINGS['EMAIL_HOST_USER']=parmdict.get('emailHostUser')
            if len(parmdict.get('emailHostPassword')) > 0:
                self.SETTINGS['EMAIL_HOST_PASSWORD']=parmdict.get('emailHostPassword')
            self.SETTINGS['EMAIL_PORT']=int(parmdict.get('emailHostPort'))
            self.SETTINGS['EMAIL_USE_TLS']=bool(parmdict.get('emailUseTLS'))
        if backend == 'django.core.mail.backends.filebased.EmailBackend':
            self.SETTINGS['EMAIL_FILE_PATH']=parmdict.get('emailFilePath')
#        self.SETTINGS['DEBUG']=bool(parmdict.get('debug'))
        self.SETTINGS['LOG_LEVEL']=int(parmdict.get('log_level'))
      
    def setParm(self, settings_name, options_name, options_type, **options):
        parm=options[options_name]
        if None == parm:
            return
        if options_type == 'int':
            parm=int(parm)
        elif options_type == 'bool':
            parm=bool(parm=='True')
        self.SETTINGS[settings_name]=parm
        
    def setValuesFromOptions(self, **options):
        """
        setup the SETTINGS dictionary from the values given by the commandline-options
        :param parmdict: settings returned from form
        """
        self.setParm('EMAIL_BACKEND','email_backend','str',**options)
        backend=self.SETTINGS['EMAIL_BACKEND']
        if backend == 'django.core.mail.backends.smtp.EmailBackend':
            self.setParm('EMAIL_HOST', 'email_host', 'str',**options)
            self.setParm('EMAIL_HOST_USER', 'email_host_user', 'str',**options)
            self.setParm('EMAIL_HOST_PASSWORD', 'email_host_password', 'str',**options)
            self.setParm('EMAIL_PORT', 'email_host_port', 'int',**options)
            self.setParm('EMAIL_USE_TLS', 'email_use_tls', 'bool',**options)
        if backend == 'django.core.mail.backends.filebased.EmailBackend':
            self.setParm('EMAIL_FILE_PATH','email_file_path','str',**options)
        self.setParm('LOG_LEVEL','log_level','bool',**options)

    def presence(self) -> bool:
        """
        Check if the local settings file already exists
        """
        logging.debug("Looking for settings-file: "+self.LOCAL_SETTINGS_File)
        if os.path.exists(self.LOCAL_SETTINGS_File) & os.path.isfile(self.LOCAL_SETTINGS_File):
            return True
        else:
            return False
        
    def read(self):
        """
        Read the local settings file and copy its contents into the
        local SETTINGS
        """
        try:
            self.lsfile=open(self.LOCAL_SETTINGS_File,"r")
        except FileNotFoundError:
            return #use given defaults
        if self.lsfile.mode == 'r':
            lines=self.lsfile.readlines()
            for line in lines:
                for item in self.SETTINGS.keys():
                    if item in line:
                        contents = line.split(" = ")
                        if item != contents[0]:
                            continue
                        if type(self.SETTINGS[item]) is str:
                            self.SETTINGS[item]=str(contents[1]).strip().strip("'")
                        elif type(self.SETTINGS[item]) is int:
                            self.SETTINGS[item]=int(contents[1])
                        elif type(self.SETTINGS[item]) is bool:
                            self.SETTINGS[item]=contents[1]=="True\n"
                        else:
                            raise Exception
                        break
        self.close()
                        
            
    def save(self):
        """
        Save anything held in local SETTINGS to a fresh created local settings file
        """
        self.lsfile=open(self.LOCAL_SETTINGS_File, "w+")
        for item in self.SETTINGS.keys():
            if type(self.SETTINGS[item]) is str:
                self.lsfile.write(item + " = '" + str(self.SETTINGS[item]) + "'\r\n")
            elif type (self.SETTINGS[item]) is int:
                self.lsfile.write(item + " = " + str(self.SETTINGS[item]) + "\r\n")
            elif type(self.SETTINGS[item]) is bool:
                self.lsfile.write(item + " = " + str(self.SETTINGS[item]) + "\r\n")
            else:
                raise Exception
        self.close()
           
    
    def close(self):
        """
        Close the local settings file
        """
        self.lsfile.close()
        
    def remove(self):
        """
        Delete the local settings file
        """
        self.setDefaults()
        try:
            os.remove(self.LOCAL_SETTINGS_File)
        except:
            return 
        return  
    
class PasswordField(forms.CharField):
    """
    Specific field with password-formatting setup properly
    """
    widget = forms.PasswordInput()
    
class settingsForm(forms.Form):
    """
    Create the form fields for the settings view
    """
        
    def get_urlType(self,url):
        pos=url.find('://')
        return url[:pos-1]
    def get_urlUser(self,url):
        pos=url.find('://')
        pos_at=url.find('@')
        return url[pos+3:pos_at]
    def get_urlIP(self,url):
        pos_at=url.find('@')
        pos_end=url.find('//',pos_at)
        return url[pos_at+1:pos_end]
    settingsObject=local_settings()
    settingsObject.read()
    backendlist = (
        ('django.core.mail.backends.smtp.EmailBackend',_('Usual email')),
        ('django.core.mail.backends.console.EmailBackend',_('Email to console')),
        ('django.core.mail.backends.filebased.EmailBackend',_('Email to file')),
    )
    loglevellist = (
        (logging.DEBUG,_('Debug infos')),
        (logging.INFO,_('Details')),
        (logging.ERROR,_('All errors')),
        (logging.CRITICAL,_('Critical errors only')),
        (logging.FATAL,_('Fatal errors only')),
    )
    
    emailBackend = forms.ChoiceField(label=_("Backend"), choices=backendlist, initial=settingsObject.SETTINGS["EMAIL_BACKEND"], required=True)
    emailHost = forms.GenericIPAddressField(label=_("Host"), initial=settingsObject.SETTINGS["EMAIL_HOST"], required=False)
    emailHostUser = forms.CharField(label=_("Login User"), initial=settingsObject.SETTINGS["EMAIL_HOST_USER"], required=False)
    emailHostPassword = PasswordField(label=_("Login user password"), required=False)
    emailHostPort = forms.IntegerField(label=_("Port"), initial=settingsObject.SETTINGS["EMAIL_PORT"], required=False)
    emailUseTLS = forms.BooleanField(label=_("Using TLS?"), initial=settingsObject.SETTINGS["EMAIL_HOST"], required=False)
    emailFilePath = forms.FilePathField(label=_("Path for email-file to be written"), path = settingsObject.SITE_ROOT ,initial=settingsObject.SETTINGS["EMAIL_FILE_PATH"], recursive=True, allow_folders=True, allow_files=False, required=False)
#    debug = forms.BooleanField(label=_("Turn on debug/not for production!"),initial=settingsObject.SETTINGS["DEBUG"], required=False)
    log_level = forms.ChoiceField(label=_("Logging level"), choices=loglevellist, initial=settingsObject.SETTINGS["LOG_LEVEL"], required=True)
    
