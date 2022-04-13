#!/bin/bash
  
#
# kommentiert einen Part in util.py Files aus
# wird im djnsr/makefile verwendet
#
# Pattern zwischen dem auskommentiert werden soll
#       MAKEMIGRATIONS_ERROR
#

fname=$1
todo=$2
SECOND=$3 # Second Time (zwei Bereiche müssen maskiert werden)
THIRD=$4 # Third Time (drei Bereiche müssen maskiert werden)

if [ "$todo" == "IN" ]; then
    ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR
ka
/
ke
'a,'es/^/#/
wq
HERE

# SECOND
    if [ ${SECOND} -eq 1 ]; then
        ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR2
ka
/
ke
'a,'es/^/#/
wq
HERE
    fi
# THIRD
    if [ ${THIRD} -eq 1 ]; then
        ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR3
ka
/
ke
'a,'es/^/#/
wq
HERE
    fi

else
    ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR
ka
/
ke
'a,'es/^#//
wq
HERE

# SECOND
    if [ ${SECOND} -eq 1 ]; then
        ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR2
ka
/
ke
'a,'es/^#//
wq
HERE
    fi
# THIRD
    if [ ${THIRD} -eq 1 ]; then
        ed ${fname} << HERE
/MAKEMIGRATIONS_ERROR3
ka
/
ke
'a,'es/^#//
wq
HERE
    fi
fi
