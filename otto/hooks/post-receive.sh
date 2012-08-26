#!/bin/bash
# TODO Write the post-receive hook!
set -e # exit immediately on error

# First, figure out how to navigate to the workspace.
# Git hooks drop you in the .git dir of your repo, setting $GIT_DIR=.
REPO=$(dirname `pwd`)
BASENAME=`basename $REPO`
cd ../../../
OTTO_HOME=`pwd`
cd workspace/$BASENAME

# Must change the GIT_DIR or these commands will operate on the wrong repo.
# Do it in a sub-shell just in case.
(
GIT_DIR=.git

# Get latest code
git fetch

# Determine the latest otto-* tag.
TAG=git tag -l otto-* | sort | awk 'END {print}'

# Install checkout latest tag, trashing local changes
git reset --hard $TAG

# Calculate the right virtualenv and activate
ENVHASH=md5sum requirements.txt | awk {print $1}
source $OTTO_HOME/virtualenvs/$ENVHASH/bin/activate

fab build web.golive
)
