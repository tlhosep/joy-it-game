#!/bin/bash

PIP="pip3"
PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`
NONRASPI=$1


"$PYTHON" --version &> /dev/null 
if [ $? != 0 ]; then
	PYTHON="python"
else
	echo "using $PYTHON"
fi

setVirtEnv() {
	PYTHON="$PWD/$ENVNAME/bin/$PYTHON"
	. "$PWD/$ENVNAME/bin/activate"
	if [ $? == 0 ]; then
		echo "$ENVNAME activated"
		echo "Using $PYTHON"
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

echo "emulate keyboard pressed..."
"$PYTHON" manage.py emulate_key $1
