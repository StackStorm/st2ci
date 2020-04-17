#!/bin/bash
set -e

df -h

if  [ -n "$(command -v yum)" ]; then
    echo ">> Detected yum-based Linux"
	sudo yum clean all
fi

if [ -n "$(command -v apt)" ]; then
    echo ">> Detected apt-based Linux"
	sudo apt-get clean
	sudo apt-get autoremove --purge
fi

df -h
