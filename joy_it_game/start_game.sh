#!/bin/bash


PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`
NONRASPI=$1
NOAPPSTART=$2

echo "Game started with parameters 1:$NONRASPI 2:$NOAPPSTART"

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


if [ "$NOAPPSTART" == "" ]; then
	echo "starting the web-server..."
	"$PYTHON" manage.py runserver &
	echo $! > ./tlu_pid

	sleep 7s
	
	echo "Opening the browser to show the app..."
	xdg-open --help &> /dev/null
	if [ $? == 0 ]; then
		xdg-open http://127.0.0.1:8000/tlu_joyit_game & &> /dev/null
		echo "App started in browser, please continue there..."
	else
	
		open http://127.0.0.1:8000/tlu_joyit_game &> /dev/null
		echo "Please see browser :)"
	fi

fi
read -p "Press Enter to close this window"

