#!/bin/bash
#
#   Script zum Setzen der Version in den __init__.py Files
#   Das Script wird im Normalfall vom "make" aufgerufen
#
#   Das Setzen der eigentlichen Version-Nr. sollte folglich im
#   makefile erfolgen
#

INIT_FILES="./hilgi/__init__.py"

for f in ${INIT_FILES}; do
    ed $f <<HERE
/Version
s/= "[0-9.]*"/= "$1"
w
q
HERE

done

ed docker-compose.yml <<HERE
/image: hilgi
s/hilgi:.*/hilgi:$1/
w
q
HERE
