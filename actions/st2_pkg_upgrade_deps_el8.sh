#!/bin/bash
set -e

VERSION=$1
ENTERPRISE=$2
SHORT_VERSION=`echo ${VERSION} | cut -d "." -f1-2`

# Placeholder for the version-to-version st2 scripted updates
#if [ ${SHORT_VERSION} = "2.4" ] && [ ${ENTERPRISE} -eq 0 ]; then
#    echo "Upgrading dependencies for 2.4 community"
#    exit 0
#fi
