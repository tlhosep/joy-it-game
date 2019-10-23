#!/bin/bash

PIP="pip3"
PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`
ADAFRUIT_PATH="adafruit"
NONRASPI=$1

echo "Trying to download the most recent version of the game..."
echo "$PWD" | grep "joy-it-game/joy_it_game" > /dev/null
if [ $? != 0 ]; then
	echo "Please cd into the directory containing this shell-script and try again"
	exit 1
fi
git pull
if [ $? == 0 ]; then
	echo "Your game is now up to date!"
	echo "next we check for deployed packages and potential database updates..."
else
	echo "The update failed somehow, please read the instructions on top..."
	echo "it might help to force an update via these 2 lines:"
	echo "$ git fetch --all"
	echo "$ git reset --hard origin/master"
	exit 1
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
#checkModule "pynput"
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
#	checkPackage "rabbitmq-server"
else
	checkModule "fake-rpi" "mandatory" "git+https://github.com/sn4k3/FakeRPi" "sudo"
fi

echo "Migrate, just in case... (will also create the db)"
"$PYTHON" manage.py migrate
if [ $? != 0 ]; then
	echo "Something went wrong with the deployment, please try again..."
	exit 1
fi

echo "update of game finished!"
