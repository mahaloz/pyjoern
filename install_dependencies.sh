#!/bin/bash

[ "$(uname)" == "Darwin" ] && IS_MACOS=1 || IS_MACOS=0

echo "Installing system dependencies: graphviz, openjdk-19, unzip..."
if [ $EUID -eq 0 ]
then
    export SUDO=
else
    export SUDO=sudo
fi
if [ -e /etc/debian_version ]
then
    $SUDO apt-get update -y
    $SUDO apt-get install -y graphviz-dev openjdk-19-jdk unzip
elif [ $IS_MACOS -eq 1 ]
then
    if ! which brew > /dev/null;
    then
        error "You must have homebrew installed for MacOS installs."
    fi
    brew install graphviz-dev openjdk@19 unzip
else
    error "System is unknown, please install graphviz-dev on your system!"
fi