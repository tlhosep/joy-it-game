#!/bin/bash

pid_file="./tlu_pid"
ENVNAME="pythongame"
PWD=`pwd`
NONRASPI=$1

get_pid() {
    if [ -f "$1" ]; then
    	cat "$1"
    else
    	echo "-1"
    fi
}

is_running() {
    [ -f "$1" ] && ps -p `get_pid $1` > /dev/null 2>&1
}

if is_running "$pid_file" ; then
	echo -n "Stopping python..."
    if [ -f "$pid_file" ]; then
 	   kill `get_pid $pid_file`
 	fi
   	for i in 1 2 3 4 5 6 7 8 9 10
    # for i in `seq 10`
    do
        if ! is_running "$pid_file"; then
            break
        fi
        echo -n "."
        sleep 1
    done
    echo

    if is_running "$pid_file" ; then
        echo "Not stopped; may still be shutting down or shutdown may have failed"
        exit 1
    else
        echo "Stopped"
        if [ -f "$pid_file" ]; then
            rm "$pid_file"
        fi
        echo "Killing remaining Python processes..."
        killall -9 Python
        killall -9 python3
        killall -9 xdg-open
    fi
else
    echo "Not running"
fi
