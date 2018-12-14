#!/bin/bash
set -e

VERSION=$1
ENTERPRISE=$2
SHORT_VERSION=`echo ${VERSION} | cut -d "." -f1-2`

if [ ${SHORT_VERSION} = "2.10" ] && [ ${ENTERPRISE} -eq 0 ]; then
    echo "Upgrading Node.js repositories"
    sed -i.bak 's|^baseurl=\(https://rpm.nodesource.com\)/[^/]\{1,\}/\(.*\)$|baseurl=\1/pub_10.x/\2|g' /etc/yum.repos.d/nodesource-*.repo
    echo "Upgrading dependencies for 2.10 community"
    sudo yum clean all
    sudo yum update -y nodejs
    exit 0
fi

if [ ${SHORT_VERSION} = "2.4" ] && [ ${ENTERPRISE} -eq 0 ]; then
    echo "Upgrading dependencies for 2.4 community"
    curl -sL https://rpm.nodesource.com/setup_6.x | sudo -E bash -
    sudo yum clean all
    sudo yum update -y nodejs
    exit 0
fi

if [ ${SHORT_VERSION} = "2.4" ] && [ ${ENTERPRISE} -eq 1 ]; then
    echo "Upgrading dependencies for 2.4 enterprise"
    sudo /opt/stackstorm/st2/bin/pip install \
        --find-links /opt/stackstorm/share/wheels --no-index --quiet \
        --upgrade st2-enterprise-auth-backend-ldap
    exit 0
fi
