#!/bin/bash
# TODO Write the post-receive hook!
set -e # exit immediately on error

# First, figure out how to navigate to the workspace.
# Git hooks drop you in the .git dir of your repo, setting $GIT_DIR=.
REPO=$(dirname `pwd`)
BASENAME=`basename $REPO`
cd ../../../workspace/$BASENAME

# Must change the GIT_DIR or these commands will operate on the wrong repo.
# Do it in a sub-shell just in case.
(
GIT_DIR=.git
# Determine the latest otto-* tag.
git fetch
TAG=git tag -l otto-* | sort | awk 'END {print}'
git reset --hard $TAG
fab build web.rsync web.install_etc
)
