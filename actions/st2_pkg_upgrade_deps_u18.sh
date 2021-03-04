#!/bin/bash
set -e

VERSION=$1
SHORT_VERSION=`echo ${VERSION} | cut -d "." -f1-2`

if [ ${SHORT_VERSION} = "2.10" ]; then
    echo "Upgrading dependencies for 2.10 community"
    curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
    exit 0
fi

if [ ${SHORT_VERSION} = "2.4" ]; then
    echo "Upgrading dependencies for 2.4 community"
    curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
    exit 0
fi
