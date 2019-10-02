""" module: cms_menus
** Content **
This module provides the menu for the web-interface

** Details **

@author: (c) Thomas Lüth 2019 / info@tlc-it-consulting.com
@created: 2019-07-28
""" 

from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool
from django.utils.translation import ugettext_lazy as _


class tlu_Menu(Menu):
    '''
    Class for the menu-handling
    '''

    def get_nodes(self, request):
        '''
        produce the node-infrastructure for the menu.
        Will be rendered in the view 
        :param request: The http-request, needed to check for login and user name
        '''
        nodes = []
        n1 = NavigationNode(_('About me'), "https://tlc-it-consulting.com/index.php/de/ueber-mich", 1)
        n2 = NavigationNode(_('Home'), "/tlu_polltest/", 2)
        if request.user.is_authenticated:
            n3 = NavigationNode(request.user.username, "/", 3)
        else:
            n3 = NavigationNode(_("Settings"), "/", 3)
            
        n4 = NavigationNode(_('email settings'), "/tlu_polltest/emailsettings", 4, 3)
        n5 = NavigationNode(_('change password'), "/accounts/password_change/", 5, 3)
        n6 = NavigationNode("#DIVIDER#","/",6, 3)
        n6_1 = NavigationNode(_('login'), "/accounts/login/", 7, 3)
        n6_2 = NavigationNode(_('logout'), "/accounts/logout/", 8, 3)
        nodes.append(n1)
        nodes.append(n2)
        nodes.append(n3)
        nodes.append(n4)
        nodes.append(n5)
        nodes.append(n6)
        loggedIn=False
        if request is not None:
            if request.user is not None:
                loggedIn=request.user.is_authenticated

        if loggedIn:
            nodes.append(n6_2)
        else:
            nodes.append(n6_1)
            
        return nodes

menu_pool.register_menu(tlu_Menu)