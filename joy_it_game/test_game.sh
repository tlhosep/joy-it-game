#!/bin/bash


PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`

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


echo "Starting the tests..."
"$PYTHON" manage.py test -v 2

