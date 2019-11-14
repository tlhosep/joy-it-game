# joy-it-game
A little game for the joy-it raspi box. It is Django/Python based and uses many of the supplied features of the box.
The main intention is to make use of the many options the box supplies and to have some fun :)
The idea of the game is to disarm a virtual bomb. So each level has some time-restrictions, once reached the level has to be played again.

## Preconditions
The software has been tested on a Joy-it experimental box using an raspberry 3B+ board.
Other boards have not been checked, the software needs some resources as we start a 
web-server to get started.
You may test if the system also runs with less capable raspberry boards, but there 
is no warranty that you will succeed.

## Installation
(see further below for more details)
1. Start the experimental box
2. Open a terminal
3. cd to the Desktop
4. mkdir GAME or equivalent (name does not count)
5. cd GAME
6. download the code from github: git clone https://github.com/tlhosep/joy-it-game
7. Once completed cd to joy-it-game/joy_it_game
8. run ./deploy_game.sh (may take a while)
9. Note down the chosen admin-account and its password in case you may later on need it. (The user 'admin' with Password xxx has now been created and could be used to administer the system. Please note this down.)
10. Make your settings for email (console is preferred) and logging (errors is the preferred choice)
11. Check that the email did work (usually shown on the console)
12. You should then see "deployment of game finished!"
13. That's all

## Start
Double-Click on the Desktop-Icon to start the little game. The browser will start and will provide you with a startup screen.
Please register yourself in order to save some results and then start the game.

## Dip-settings
For each of the steps to mitigate the "bomb" please check the Dip-settings as they 
are displayed. If they are not correct, the game-level could not be played.

*Have fun!*

## Updating the game
If needed you may want to update to the most recent version of the game. This is very easily done. Please proceed as follows:
1. Start the experimental box
2. Open a terminal
3. cd to the Desktop/GAME/joy-it-game/joy_it_game  (in case you have chosen GAME as teh initial folder on the Desktop)
4. enter as follows: ./update_game

You will be guided through the steps to update the game automatically, usually there is no user-intervention needed.

## Detailed deployment

You could start like this:
![alt text](https://github.com/tlhosep/joy-it-game/blob/master/joy_it_game/assets/screen_joyit_deployment_start.jpg)

On the commandline enter as follows:
```
pi@raspberrykoffer:~ $ cd Desktop/
pi@raspberrykoffer:~/Desktop $ mkdir GAME
pi@raspberrykoffer:~/Desktop $ cd GAME/
pi@raspberrykoffer:~/Desktop/GAME $ git clone https://github.com/tlhosep/joy-it-game
pi@raspberrykoffer:~/Desktop/GAME $ cd joy-it-game/joy_it_game
pi@raspberrykoffer:~/Desktop/GAME/joy-it-game/joy_it_game $ ./deploy_game.sh 
…
deployment of game finished!
pi@raspberrykoffer:~/Desktop/GAME/joy-it-game/joy_it_game $
```
While running the deployment please note down this important line:
![alt text](https://github.com/tlhosep/joy-it-game/blob/master/joy_it_game/assets/screen_joyit_deployment_admin.png)
You should note down the admin user and its password in order to administer the user and the game later on.

Once deployment finished it results in this desktop:
![alt text](https://github.com/tlhosep/joy-it-game/blob/master/joy_it_game/assets/screen_joyit_deployment_done_commented.jpg)
1) Localized setting-questions (in this case in German): You have to specify the email system (use console unless you have other plans) and a logging level (errors should do)
2) In case you have chosen console for the email subsystem, you will see this email. In case of other choices you may specify a path to store the email-file or specify settings of your email-server taht is going to deliver the emai to you. In the later case you also have to specify the content and receiver of the test-email
3) Please check the email and select "Yes" to confirm that you have received the email
4) This is the final message, once seen we are sure that everything went as it should :)

You will then note the 2 new icons on the desktop. These are the ones to click to start and to end the game.
When the game started a commandline window is left open. Once you have closed the browser, please press the ENTER-key once you have the commandline window active in order to close it. This is going to shut down the web-server and the game itself.

# Development and structures
## Environment
I decided to use eclipse (currently I am using the version 2019-09 R (4.13.0) ) and the Python development plugins. This is a very good start :)

## Some words about the structure of the implementation
```
.
├── accounts
│   └── migrations
├── assets
├── docs
│   ├── joy_it_game
│   ├── tlu_django_test
│   ├── tlu_game
│   ├── tlu_hardware
│   ├── tlu_joyit_game
│   └── tlu_services
├── joy_it_game
├── locale
│   └── de
├── log
├── pythongame
│   ├── bin
│   ├── include
│   └── lib
├── tlu_game
├── tlu_hardware
├── tlu_joyit_game
│   ├── management
│   ├── migrations
│   └── templates
├── tlu_services
└── webdesign
```
- accounts contains functionalities that manage the user
- assets provides some images for this readme and the desktop
- docs contains the pycco generated documentation
- joy_it_game is the main start and contains all teh needed settings
- locale contaimns the translations (currently we support German and English)
- log holds the game.log file
- pythongame is the local Python structure for all needed modules (will be generated by the deployment script)
- tlu_game is the main place for all the levels of the gamme
- tlu_hardware holds all hardware-specific supportfiles and libraries
- tlu_joy_it_game is the main place for all views, all templates and forms
- tlu_services do provide some helpful wrapper for process- and thread-management as well as for emails
- webdesign holds the "source" for bootstrap sdtudio that I have used to create the bootstrap templates

## Commandline tools
The following commandline tools are provided:

| Shell-tool | Actions performed |
| :---- | :----------------- |
| compile_po.sh | compile (generate the mo-file) the given and edited .po file for the languages supported |
| deploy_game.sh | Deploy the game, you have used this before :) |
| gen_doc.sh | generates the pycco documentation |
| gen_po.sh | generates a new or updated po file for your translations |
| modify_settings.sh | Modify the local settings file |
| start_game.sh | will be called when the user clicks on the Desktop-Icon to start the game |
| start_kbdinput.sh | starts a commandlien-shell to simulate the hardware-keys (usefull for debugging on the Mac) |
| stop_game.sh | opposite to start_game.sh |
| test_game.sh | runs the provided testcases |
| update_game.sh | Once a new version arrived on github, you could start this script to obtain amd deploy it. |

## Game structure
The view starts the "usual" game-level view and in the background we use a process for each level. The decision had been taken as we needed to make sure that the level could be terminated even really hard when running wild. A thread could not be really terminated... Threads we use for the several hardware-bound activities.

Please note that we have to use BCM for addressing the hardware as some libraies need exact this address-scheme...

All the threads communicate via message-queues (Fifo) and when using the keyboard emulation on Mac this is also using the remote queue to forward the pressed keys to the game. 

The Web-frontent contains some Javascripts to start a json-call in order to show messages and updates on the screen. These are provided by soem global structures within the backend of the game.

## New levels
Adding new levels is fairly easy. 
1) I usally start by checking if a new hardware is needed. If so, I create some scripts and the respective test-case(s). I usually do this by copying some existing py-scripts and modify them as needed. Please note that a new hardware needs usually a change to the hardwarebase file as all addresses and ports are stored there.
2) Then we have to setup the level-template (tlu_joyit_game/templates/tlu_joyit_game) by copying an existing one.
3) The game-logic is the trickiest part. Please check existing levels (see tlu_game) and use any of the existing ones as the base for your implementation. Please keep the naming-convention: tlu_level directly followed by the level-number as two decimals (eg. tlu_level12)
4) The new level has to made visible to the model (tlu_joyit_game/models.py). In the class "Game", scroll down to the "frequent_updates" and add a number (in milliseconds) that the frintend shall wait before callimng the backend again.
5) In the same file and also in the calss "Game" you have to add the needed dipswitch_settimgs (in the __init__ method) as an logical or of all hardware-modules that come to play for your level. Each hardware provides the needed settings.
6) Now we have to add the new level to the view. Open tlu_joyit_game/views.py and scrolldown to "levels=(" Add here your new level.
7) Run the Django tests to make sure your new hardware works as you want ist to
8) Start the Django WebServer and play the game :)


