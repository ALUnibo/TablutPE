#!/bin/bash

if [[ $#  -ne 3 ]] ; then
   echo "Need all arguments"
   echo "WHITE or BLACK as first parameter"
   echo "timeout as second parameter"
   echo "server IP as third parameter"
   echo "Example: $0 WHITE 60 192.168.20.254"
   exit 1
fi

python3.10 /home/tablut/tablut/TablutPlayer/main.py "$1" "$2" "$3"
