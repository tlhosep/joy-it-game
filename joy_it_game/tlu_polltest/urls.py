""" module: urls
** Content **
This module holds all teh used URLs of the game 

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-09 
"""

from django.urls import path
from tlu_services import tlu_local_settings

from . import views
from django.urls.conf import re_path

app_name = 'tlu_polltest'
urlpatterns = [
    # index is the same as the default view (blank)
    path('index', views.IndexView.as_view(), name='index'),
    # form to log-in
    path('login', views.LoginView.as_view(), name='login'),
    #following is the setting and checksettings section (forms)
    path('settings', views.settings, name='settings'),
    path('settingscheck', views.settings_check, name='settingscheck'),
    path('emailsettings', views.SettingsView.as_view(), name='emailsettings'),
    path('emailsettingscheck', views.SettingsCheckView.as_view(), name='emailsettingscheck'),
    # demo-page (static, no login needed)
    path('demo', views.DemoView.as_view(), name='demo'),
    # some levels / the game
    path('restart', views.restart, name='restart'), #start from the beginning
    path('levelOverview', views.LevelOverview, name = 'levelOverview'),
    path('level/<int:level_id>', views.LevelView, name='level'),
    path('start/<int:level_id>', views.startlevel, name='start'),
    path('abort/<int:level_id>', views.abortlevel, name='abort'),
    path('retry/<int:level_id>', views.retrylevel, name='retry'),
    re_path(r'^ajax/level_update/$', views.level_update, name='level_update'),
    path('deletelevel/<int:level_id>', views.deletelevel, name='deletelevel'),
    
    # following are some sample-urls for understanding Django ;)
    # ex: /tlu_polltest/5/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /tlu_polltest/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /tlu_polltest/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
]

# below logic is needed to show up a config page at first startup to set some mail-settings for the user-handling
settings=tlu_local_settings.local_settings()
if tlu_local_settings.local_settings.presence(settings):
    startuppath=path('', views.IndexView.as_view(), name='index_main')
else:    
    startuppath=path('', views.SettingsView.as_view(), name='setup')
    
# add the respective correct path to the list of urls  
urlpatterns.insert(0, startuppath)
