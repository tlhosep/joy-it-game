""" module: views
** Content **
Main functionality of the Web interface. 

** Details **
Contains the major functions to run the game and the background methods to provide the 
content for specific pages.

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-10-01 
""" 
from django.shortcuts import render, get_object_or_404, render_to_response
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormView
from tlu_services import tlu_local_settings, tlu_local_settings_check
from django.utils.translation import gettext as _
from django.http.response import HttpResponseNotAllowed, JsonResponse
import logging
import smtplib
from tlu_joyit_game.models import Level, getGameState, setGameState
from django.template.defaulttags import register
from django.contrib.auth.models import User
from joy_it_game import settings
from tlu_game.tlu_level00 import Level00
from tlu_game.tlu_level01 import Level01
from tlu_game.tlu_level02 import Level02
from tlu_game import tlu_globals
from tlu_game.tlu_level03 import Level03
from tlu_hardware import tlu_hardware_global
from tlu_hardware.tlu_hardwarebase import tlu_hardwarebase

logfile=settings.BASE_DIR+"/log/game.log"
logger = logging.getLogger(__name__)
 
# List of levels that form the game, the first level (00) is for internal testings only! 
# Please make sure to update "models.py" as well for the level
levels=(Level00,Level01,Level02,Level03)

def suspendCurrentGame(request):
    """
    Terminate current level played asap
    :param request: HTTP-Call
    """
    user=request.user
    try:
        game=user.game
    except:
        return
    if game.is_running():
        game.abort()
        game.save()

class IndexView(generic.TemplateView):
    """
    Main View/startscreen
    """
    template_name = 'tlu_joyit_game/index.html'
        
    def get(self, request, *args, **kwargs):
        """
        Renders the view and starts the hardware by displaying the clock
        Kills as well all possible running processes
        :param request: HTTP-request
        """
        logger.info("Index View called")
        tlu_globals.init()
        tlu_hardware_global.init()
        suspendCurrentGame(request)
        level=Level00(request.user.id)
        level.cleanup(True)
        level.startup()  
        tlu_globals.globMgr.tlu_glob().stopClock()
        return generic.TemplateView.get(self, request, *args, **kwargs)
    
class DemoView(generic.TemplateView):
    """
    Demo-screen / work in progress
    """
    template_name = 'tlu_joyit_game/demo.html'
  
@register.filter(name='levelConvert')
def get_resultname(key) -> str:
    """
    Show the name of the result on the screen, returns the name as string
    :param key: result of the level (number)
    """
    if (key==None):
        return ""
    return Level.resultdict[key]

@register.filter(name='totalTime')
def get_totaltime(level) -> str:
    """
    Calculate the total time needed for the level as a string
    :param level:
    """
    if (level == None) or (level.level_start == None) or (level.level_ended == None):
        return "0"
    return str((level.level_ended-level.level_start).total_seconds())
    
    
def LevelOverview(request):
    """
    Render the Level-overwiew which contains a table for the current state and 
    as well another one for the levels played so far.
    
    :param request: HTTP-request
    """
    if request.method=='GET':
        tlu_globals.init()
        tlu_hardware_global.init()
        suspendCurrentGame(request)
        level=Level00(request.user.id)
        level.startup()  
        template_name = 'tlu_joyit_game/level_overview.html'
        user=get_object_or_404(User, pk=request.user.id)
        game=user.game
        logging.debug("LevelOverview, current game="+str(game))
        button_text=_("Continue the game now")
        path=""
        try:
            level_set=game.level_set.all().order_by('-id')
        except (KeyError, Level.DoesNotExist):
            level_set=None
        cur_level=game.current_level
        if cur_level == None:
            current_level_num=0
        else:
            current_level_num = cur_level.levelnum
        next_level_num = current_level_num
        if (cur_level != None) and (cur_level.result == Level.PASSED):
            next_level_num += 1
            if game.completed(next_level_num):
                next_level_num -= 1
                button_text=_("Play level again")
                path=reverse('tlu_joyit_game:retry', kwargs={'level_id':next_level_num})
        if len(path) == 0:
            path=reverse('tlu_joyit_game:level', kwargs={'level_id':next_level_num})
        last_played=None
        if (cur_level != None):
            last_played=cur_level.level_start
        if last_played == None:
            last_played=_("Not yet played")
            path='/tlu_joyit_game/restart'
        if (level_set == None) or (len(level_set)<1):
            button_text=_("Start now")
        achieved_points=request.user.game.getAchievedPoints()
        return render(request, template_name, {'levellist':level_set, 
                                               'current_level': str(current_level_num), 
                                               'last_played': last_played,
                                               'achieved_points':achieved_points,
                                               'no_levels':(level_set==None) or (len(level_set)<1),
                                               'button_text':button_text,
                                               'next_level_url' : path})
    return HttpResponseNotAllowed(['POST'])

def restart(request):
    """
    Process the restart request from the user
    :param request: HTTP-request
    """
    tlu_globals.init()
    tlu_hardware_global.init()
    game=request.user.game
    game.restart()
    return HttpResponseRedirect(reverse('tlu_joyit_game:level', kwargs={'level_id':1}))

class OutOfRangeError(Exception):
    """
    Class to specify that the level is not within the allowed range
    """
    pass

def checkLevel(request, level_id):
    """
    Check that the provided level is within the allowed range.
    If not raises an OutOfRangeError
    :param request: HTTP-request
    :param level_id: level-number (picked from url)
    """
    if level_id == 1:
        #startup level is ever ok
        return
    user=request.user
    try:
        tlu_globals.init()
        tlu_hardware_global.init()
        game=user.game
    except:
        return
    if game.current_level == None:
        if (level_id > 1):
            status=getGameState(user.id)
            status.msg=_("You just started from the beginning, so level has to be one, please restart the game!")
            setGameState(user.id,status)
            raise OutOfRangeError
        else:
            return
    if (level_id > game.current_level.levelnum +1) or (level_id < game.current_level.levelnum) or game.completed(level_id):
        status=getGameState(user.id)
        status.msg=_("The requested level is not in line with our expectations, please restart the game!")
        setGameState(user.id,status)
        raise OutOfRangeError
    
def renderLevel(request, level_id):
    """
    Show the Level-page where we can start the individual level
    :param request: HTTP-request
    :param level_id: level-number to start
    """
    template_name = "level_"+"{:02d}".format(level_id)+".html"
    user=request.user
    game=user.game
    try:
        tlu_globals.init()
        tlu_hardware_global.init()
        checkLevel(request, level_id)
    except OutOfRangeError:
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id does not fit your overall progress, you have to restart.")
        return render(request, template_name, {'error':error} )
    dips = game.getDipSwitch(level_id)
    leftDip=_("left:")+" "+tlu_hardwarebase.showleft_dip(dips)
    rightDip=_("right:")+" "+tlu_hardwarebase.showright_dip(dips)
    overall_progress=game.getOverallProgress()
    info=_("Please press start and check the DIP-settings...")
    button_text=_("Start Level")+" "+str(level_id)
    button_url='/tlu_joyit_game/start/'+str(level_id)
    return render(request, template_name, {'leftDip':leftDip, 
                                           'rightDip':rightDip, 
                                           'overall_progress':overall_progress, 
                                           'info':info, 
                                           'button_text':button_text,
                                           'button_url':button_url} )
   
    
def startlevel(request, level_id):
    """
    Starts the game as per request given and returns the Level via renderLevel
    :param request: HTTP-request
    :param level_id: level-number
    """
    user=request.user
    try:
        tlu_globals.init()
        tlu_hardware_global.init()
        checkLevel(request, level_id)
        user.game.start(levels[level_id], level_id)
        logging.debug("Game started: "+str(user.game))
    except OutOfRangeError:
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id does not fit your overall progress, you have to restart.")
        return render(request, template_name, {'error':error} )
    except Exception as e:
        template_name = "level_error.html"
        error=_("We are sorry, but the user has to be known/logged in, you have to restart.")+" Error: "+str(e)
        return render(request, template_name, {'error':error} )
    return renderLevel(request, level_id)

def abortlevel(request, level_id):   
    """
    Process the abort request
    :param request: HTTP-request
    :param level_id: level-id that shall be aborted
    """
    user=request.user
    try:
        tlu_globals.init()
        tlu_hardware_global.init()
        game=user.game
        checkLevel(request, level_id)
    except OutOfRangeError:
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id does not fit your overall progress, you have to restart.")
        return render(request, template_name, {'error':error} )
    except:
        template_name = "level_error.html"
        error=_("We are sorry, but the user has to be known/logged in, you have to restart.")
        return render(request, template_name, {'error':error} )
    game.abort()
    level=Level00(request.user.id)
    level.cleanup(True)
    level.startup()  
    return renderLevel(request, level_id) #redisplay the content 

def retrylevel(request, level_id):    
    """
    Process the retry-request, shows renderLevel in the end
    :param request: HTTP-request
    :param level_id: 
    """
    user=request.user
    try:
        tlu_globals.init()
        tlu_hardware_global.init()
        game=user.game
        checkLevel(request, level_id)
    except OutOfRangeError:
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id does not fit your overall progress, you have to restart.")
        return render(request, template_name, {'error':error} )
    except:
        template_name = "level_error.html"
        error=_("We are sorry, but the user has to be known/logged in, you have to restart.")
        return render(request, template_name, {'error':error} )
    level=Level00(request.user.id) #use the simplest instance
    level.startup() #all hardware to restart
    game.retry()
    return renderLevel(request, level_id) #redisplay the content to allow for restart

def LevelView(request, level_id):
    """
    Shows renderLevel for the given level-id
    :param request: HTTP-request
    :param level_id: level-id
    """
    level=Level00(request.user.id) #real level does not matter
    tlu_globals.init()
    tlu_hardware_global.init()
    level.startup() #some basic settings
    try:
        checkLevel(request, level_id) 
    except OutOfRangeError:
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id does not fit your overall progress, you have to restart.")
        return render(request, template_name, {'error':error} )
    if request.method=='GET':
        return renderLevel(request, level_id)
    return HttpResponseNotAllowed(['POST'])
 
def level_update(request):
    """
    Ajax call (via js-component) to retrieve the current status of the level in order to update the frontend
    returns json formatted data
    :param request: HTTP-request
    """
    if request.method=='GET':
        pagelevel=request.GET['level']
        user=request.user
        try:
            game=user.game
        except:
            data = {
                'info': _("The user seems to be unknown, please log in and restart"),
                'current_progress' : 0,
                'overall_progress' : 0,
                'poll':0,
                'delay_ms':1000,
                'button_text': _("log in"),
                'button_url': "/accounts/login/" }
            return JsonResponse(data)  

        logging.debug("Game update requested: "+str(game))
        status=getGameState(user.id)
        overall_progress=game.getOverallProgress()
        level=game.current_level
        current_level_num=0
        if level != None:
            current_level_num=level.levelnum
        logger.info("Updating level "+pagelevel +" Game="+str(game))
        button_text=_("Start Level")+" "+str(current_level_num)
        button_url='/tlu_joyit_game/start/'+str(current_level_num)
        info=status.msg
        if (info==None):
            info=_("No info available...")
        running=0
        if game.is_running(): 
            running=1
            button_text=_("Abort Level?")
            button_url='/tlu_joyit_game/abort/'+str(current_level_num)
        else:
            res=game.result(0.5)
            logging.debug("Game returned with result "+str(res)+" Game="+str(game))
            if res==Level.PASSED:
                #finished with success
                button_text=_("Next Level")
                button_url='/tlu_joyit_game/level/'+str(current_level_num+1)
                if game.endReached():
                    button_text=_("Restart?")
                    button_url='/tlu_joyit_game/restart'
            elif (res==Level.TIMEOUT) or (res==Level.DIDNOTFINISH):
                #timeout reached or level ende by an gamer error
                button_text=_("Retry")
                button_url='/tlu_joyit_game/retry/'+str(current_level_num)    
            else:
                #failure somehow
                info=str(_("Level failed somehow, please try again, result="))
                info+=Level.strFromResult(Level(), res)
                button_text=_("Retry Level?")
                button_url='/tlu_joyit_game/retry/'+str(current_level_num)
        data = {
            'info': info,
            'current_progress' : status.level_progress,
            'overall_progress' : overall_progress,
            'poll':running,
            'delay_ms':game.getFrequentUpdatesMs(current_level_num),
            'button_text': button_text,
            'button_url': button_url }
        return JsonResponse(data)  
    return HttpResponseNotAllowed(['POST'])

def deletelevel(request, level_id):
    """
    Delete a certain level as requested by the user on the Level-overview form
    :param request: HTTP-request
    :param level_id: level to be deleted
    """
    try:
        level = Level.objects.get(pk=level_id)
        if level.game.user == request.user:
            level.delete() #delete only if allowed ;=)
    except (KeyError, Level.DoesNotExist):
        template_name = "level_error.html"
        error=_("We are sorry, but the provided level-id is no longer available, you have to restart.")
        return render(request, template_name, {'error':error} )
    return LevelOverview(request) #redisplay the content without the level
    

def settings(request):
    """
    Settings-screen to setup the email basics
    :param request: HTTP-request
    """
    if request.method=='POST':
        form = tlu_local_settings.settingsForm(request.POST)
        if form.is_valid():
            form_dict=form.cleaned_data
            settings=tlu_local_settings.local_settings()
            settings.read()  # @UndefinedVariable
            settings.setValues(form_dict)  # @UndefinedVariable
            settings.save()  # @UndefinedVariable
            return HttpResponseRedirect(reverse('tlu_joyit_game:emailsettingscheck'))
        else:
            return render_to_response('setup.html', {'form': form})
#            return render(request, 'setup.html', {
#               'error_message': _("Some parameter are wrong, please correct and try again")
#                })
    return HttpResponseNotAllowed(['GET'])
       
def settings_check(request):
    """
    Perform a quick email-check to see if the parameter provided do fit
    :param request: HTTP-request
    """
    if request.method=='POST':
        form = tlu_local_settings_check.settingsCheckForm(request.POST)
        if form.is_valid():
            form_dict=form.cleaned_data
            if bool(form_dict.get('emailSuccess')):
                return HttpResponseRedirect(reverse('tlu_joyit_game:index'))
            try:
                if tlu_local_settings_check.checkMailOk(form_dict.get('emailSubject'), form_dict.get('emailMessage'), form_dict.get('emailFrom'), form_dict.get('emailTo')):
                    email_error=False
                    email_message = _("The Mail has been successfully transmitted! Please check your inbox or the choosen medium.")
                else:
                    email_error=True
                    email_message = _("The Mail could not be delivered!")
                   
            except smtplib.SMTPException as e:
                email_error=True
                email_message = e
            except BaseException as e:
                email_error=True
                email_message = _("We have encountered an unknown error during trying to submit the test-message: "+ str(e))
                
            return render(request,'setup_check.html', {'email_error':email_error, 'email_message':email_message, 'form':form})
                
        else:
            return render(request, 'setup_check.html', {
                'error_message': _("Some parameter are wrong, please correct and try again")
                })
    return HttpResponseNotAllowed(['GET'])


class SettingsView(FormView):
    """
    Form to get the settings
    """
    template_name="setup.html"
    form_class=tlu_local_settings.settingsForm
    success_url = 'settings'

class SettingsCheckView(FormView):
    """
    Screen to perform the email-check and to show teh result
    """
    template_name="setup_check.html"
    form_class=tlu_local_settings_check.settingsCheckForm
    success_url = 'settingscheck'

