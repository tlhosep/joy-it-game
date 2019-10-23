# joy-it-game
A little game for the joy-it raspi box. It is Django/Python based and uses many of the supplied features of the box.

## Preconditions
The software has been tested on a Joy-it experimental box using an raspberry 3B+ board.
Other boards have not been checked, the software needs some resources as we start a 
web-server to get started.
You may test if the system also runs with less capable raspberry boards, but there 
is no warranty that you will succeed.

## Installation
1. Start the experimental box
2. Open a terminal
3. cd to the Desktop
4. mkdir game or equivalent
5. cd game
6. download the code from github: git clone https://github.com/tlhosep/joy-it-game
7. Once completed cd to joy-it-game/joy_it_game
8. run ./deploy_game.sh (may take a while)
9. Note down the chosen admin-account and its password in case you may later on need 
   it. (The user 'admin' with Password xxx has now been created and could be used to administer the system. Please note this down.)
10. You should see now "deployment of game finished!"
11. That's all

## Start
Click on the Desktop-Icon to start the little game. The browser will start and will 
provide you with a screen to specify the email settings, as these may be needed in 
case you have forgotten your password ;) It is totally ok to just show them on the 
terminal/console for the start. If you prefer, you could configure your own mail-server 
here.
This action is only required once.
After that please register yourself in order to save some results and then start the 
game.

## Dip-settings
For each of the steps to mitigate the "bomb" please check the Dip-settings as they 
are displayed. If they are not correct, the game-level could not be played.

*Have fun!*

## Detailed deployment

You could start like this:
![alt text](https://github.com/tlhosep/joy-it-game/blob/master/joy_it_game/assets/screen_joyit_deployment_start.jpg)

On the commandline enter as follows:
```
pi@raspberrykoffer:~ $ cd Desktop/
pi@raspberrykoffer:~/Desktop $ mkdir GAME
pi@raspberrykoffer:~/Desktop $ cd GAME/
pi@raspberrykoffer:~/Desktop/GAME $ git clone https://github.com/tlhosep/joy-it-game
pi@raspberrykoffer:~/Desktop/GAME $ cd joy-it-game/
pi@raspberrykoffer:~/Desktop/GAME/joy-it-game/joy_it_game $ ./deploy_game.sh 
…
deployment of game finished!
pi@raspberrykoffer:~/Desktop/GAME/joy-it-game/joy_it_game $
```
This results in this desktop:
![alt text](https://github.com/tlhosep/joy-it-game/blob/master/joy_it_game/assets/screen_joyit_deployment_done_commented.jpg)

You will note the 2 new icons on the desktop. These are the ones to click to start and to end the game.
When the game started a commandline window is left open. Once you have closed the browser, please press the ENTER-key once you have the window active in order to close it.
