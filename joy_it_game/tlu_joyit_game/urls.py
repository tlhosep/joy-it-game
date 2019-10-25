""" module: urls
** Content **
This module holds all the used URLs of the game 

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-09 
"""

from django.urls import path
from tlu_services import tlu_local_settings

from . import views
from django.urls.conf import re_path

app_name = 'tlu_joyit_game'
urlpatterns = [
    # index is the same as the default view (blank)
    path('index', views.IndexView.as_view(), name='index'),
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
]

# below logic is needed to show up a config page at first startup to set some mail-settings for the user-handling
settings=tlu_local_settings.local_settings()
startuppath=path('', views.IndexView.as_view(), name='index_main')   
# add the startpath to the list of urls  
urlpatterns.insert(0, startuppath)
