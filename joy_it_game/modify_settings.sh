#!/bin/bash

PIP="pip3"
PYTHON="python3"
ENVNAME="pythongame"
PWD=`pwd`
res_file="./tlu_res"

get_res() {
    if [ -f "$1" ]; then
    	cat "$1"
    else
    	echo "1"
    fi
}

lang=$(locale | grep LANG | cut -d= -f2 | cut -d_ -f1 )
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

echo "modify and test the settings..."
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

echo "setup of game finished!"
