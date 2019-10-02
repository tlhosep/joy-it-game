""" module: forms
** Content **
This module helps to define the fields for the tables used on the Level-Overview form 

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-29 
""" 
from django import forms
from tlu_polltest.models import Game

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ('current_level', 'achieved_points', 'last_played')
        
class LevelForm (forms.ModelForm):
    class Meta:
        model = Game
        fields = ('level', 'level_start', 'level_ended', 'points', 'time_needed', 'passed')       
        