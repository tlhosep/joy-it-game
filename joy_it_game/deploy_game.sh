#!/bin/bash

PIP="pip3"
PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`
ADAFRUIT_PATH="adafruit"
NONRASPI=$1
res_file="./tlu_res"

get_res() {
    if [ -f "$1" ]; then
    	cat "$1"
    else
    	echo "1"
    fi
}

lang=$(locale | grep -w LANG | cut -d= -f2 | cut -d_ -f1 )
if [ ${#lang} > 2 ]; then
	lang=$(echo $lang | cut -c 2-3 )
fi

"$PIP" -V &> /dev/null 
if [ $? != 0 ]; then
	PIP="pip"
else
	echo "using $PIP"
fi

"$PYTHON" --version &> /dev/null 
if [ $? != 0 ]; then
	PYTHON="python"
else
	echo "using $PYTHON"
fi

setVirtEnv() {
	PYTHON="$PWD/$ENVNAME/bin/$PYTHON"
	PIP="$PWD/$ENVNAME/bin/$PIP"
	. "$PWD/$ENVNAME/bin/activate"
	if [ $? == 0 ]; then
		echo "$ENVNAME activated"
		echo "Using $PYTHON and $PIP"
	else
		echo "Failed to activate $ENVNAME"
		exit 1
	fi
	echo "trying to upgrade pip in case...."
	$PIP install --upgrade pip
}

echo "checking for virtual environment..."
if [ -d "$ENVNAME" ]; then
	setVirtEnv
	echo "$ENVNAME existed, is now active"
else
	$PYTHON -m venv "$ENVNAME"
	setVirtEnv
	echo "Created and activated $ENVNAME"
fi	

checkModule() {
	modname=$1
	optional=$2
	modulepath=$3
	sudo_required=$4
	echo "checking for $modname..."
	$PIP list --format=columns | grep $modname &> /dev/null
	if [ $? == 0 ]; then
		echo "$modname installed"
	else
		if [ "$modulepath" == "" ]; then
			if [ "$sudo_required" == "" ]; then
				"$PIP" install --upgrade "$modname"
			else
				sudo "$PIP" install --upgrade "$modname"
			fi
		else
			if [ "$sudo_required" == "" ]; then
				"$PIP" install "$modulepath"
			else
				sudo "$PIP" install "$modulepath"
			fi
		fi
		if [ $? == 0 ]; then
			echo "$modname yet deployed!"
		else
			echo "$modname could not be installed... :("
			if [ ! "$optional" == "opt" ]; then
				exit 1
			fi
		fi
	fi
}

checkAdafruit() {
	echo "checking for adafruit lcd-driver"
	if [ -d $ADAFRUIT_PATH ]; then
		echo "Adafruit seems to be deployed, skipping"
	else
		mkdir $ADAFRUIT_PATH
		cd $ADAFRUIT_PATH
		git clone https://github.com/adafruit/Adafruit_Python_CharLCD
		cd Adafruit_Python_CharLCD
		$PYTHON setup.py install
		cd ../..
		echo "Adafruit lcd-driver now deployed"
	fi		
}

createDesktopIcon() {
	DESKTOPFILE=$HOME/Desktop/joyit_game.desktop
	if [ ! -d $HOME/Desktop ]; then
		mkdir $HOME/Desktop
		echo "Desktop created"
	fi
	if [ -e $DESKTOPFILE ]; then
		echo "Desktopfile $DESKTOPFILE already exists, skipping this part..."
		return
	fi
	cat > $DESKTOPFILE << EOF
[Desktop Entry]
Name=joy-it game
Comment=Little game to demonstarte the contents of the toolbox
Icon=$PWD/assets/RB-JoyPi-2g.png
Exec=lxterminal -t "Start the game" --working-directory=$PWD -e ./start_game.sh 
Type=Application
Encoding=UTF-8
Terminal=false
Categories=None;	
EOF
	echo "Desktopfile $DESKTOPFILE created!"
}

createDesktopIconStop() {
	DESKTOPFILE=$HOME/Desktop/joyit_game_stop.desktop
	if [ ! -d $HOME/Desktop ]; then
		mkdir $HOME/Desktop
		echo "Desktop created"
	fi
	if [ -e $DESKTOPFILE ]; then
		echo "Desktopfile $DESKTOPFILE already exists, skipping this part..."
		return
	fi
	cat > $DESKTOPFILE << EOF
[Desktop Entry]
Name=Stop joy-it game
Comment=Stops the webserver
Icon=$PWD/assets/RB-JoyPi-2g-stop.png
Exec=lxterminal -t "Stop the game" --working-directory=$PWD -e ./stop_game.sh 
Type=Application
Encoding=UTF-8
Terminal=false
Categories=None;	
EOF
	echo "Desktopfile $DESKTOPFILE created!"
}

checkPackage() {
	package=$1
	optional=$2
	dpkg-query -l "$1" &> /dev/null
	if [ $? == 0 ]; then
		echo "$package already deployed!"
	else
		echo "$package will now be deployed..."
		sudo apt-get install "$package"
		if [ $? == 0 ]; then
			echo "$package yet deployed!"
		else
			echo "$package could not be installed... :("
			if [ ! "$optional" == "opt" ]; then
				exit 1
			fi
		fi
	fi
}


checkModule "peewee"
checkModule "Django"
checkModule "django-cms"
checkModule "django-bootstrap"
checkModule "PyInquirer"
if [ "$NONRASPI" == "" ]; then
	checkModule "RPi.GPIO" "opt"
	#checkModule "django-extensions" #potentially needed for the reset_db command which we for now do not use
	checkAdafruit
	checkModule "Adafruit-LED-Backpack"
	checkPackage "python3-dev"
	checkPackage "libjpeg8-dev"
	checkPackage "libpng-dev"
	checkPackage "libfreetype6-dev"
	checkModule "luma.led-matrix"
else
	checkModule "fake-rpi" "mandatory" "git+https://github.com/sn4k3/FakeRPi" "sudo"
fi

echo "Migrate, just in case... (will also create the db)"
"$PYTHON" manage.py migrate
if [ $? != 0 ]; then
	echo "Something went wrong with the deployment, please try again..."
	exit 1
fi
echo "Checking or setting the superuser..."
"$PYTHON" manage.py setup_adminuser --username=admin --email=fake@fake.com --password=test1234 --language=$lang
if [ $? != 0 ]; then
	echo "Something went wrong with the deployment, please try again..."
	exit 1
fi
echo ""
echo "IMPORTANT:"
echo "The user 'admin' with Password "test1234" has now been created and could be used to administer the system. Please note this down."
echo ""

echo "Define and test the settings..."
"$PYTHON" manage.py setup_settings --editsettings=True --language=$lang 2> $res_file
if [ $? != 0 ]; then
	cat "$res_file"
	echo "Something went wrong with the setup, please try again..."
	exit 1
fi
retvalue=`get_res "$res_file"`
while [ $retvalue == "1" ]; do
	"$PYTHON" manage.py setup_settings --language=$lang 2> $res_file
	if [ $? != 0 ]; then
		cat "$res_file"
		echo "Something went wrong with the setup, please try again..."
		exit 1
	fi
	retvalue=`get_res "$res_file"`
	if [ $retvalue == "1" ]; then
		"$PYTHON" manage.py setup_settings --editsettings=True --language=$lang 2> $res_file
		if [ $? != 0 ]; then
			cat "$res_file"
			echo "Something went wrong with the setup, please try again..."
			exit 1
		fi
		retvalue=`get_res "$res_file"`
	fi
done

rm "$res_file"


if [ "$NONRASPI" == "" ]; then
	echo "Preparing Desktop..."
	createDesktopIcon
	createDesktopIconStop
fi

echo "deployment of game finished!"
