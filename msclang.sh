#!/bin/bash
SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`
python "$(SCRIPTPATH)"/msclang.py "$@"