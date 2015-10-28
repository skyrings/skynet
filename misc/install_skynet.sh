#!/bin/bash
# This script is tested in fedora 22 server
# This is a single script which will install required packages,
# Configure and setting up the system to use skynet on storage node.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'
CWD=`pwd`

function error {
    printf "${RED}$1${NC}\n"
}

function info {
    printf "${NC}$1${NC}\n"
}

function warning {
    printf "${YELLOW}$1${NC}\n"
}

function debug {
    printf "${GREEN}$1${NC}\n"
}


# Check for the environment
if ! grep -q '^Fedora release 22 (Twenty Two)$' /etc/issue; then
    error "Currently this script support only fedora 22 server"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi


# Package installation
info "Installing necessary packages for skyring\n"
set -x
yum -y update
if [ $? -ne 0 ]; then
    error "Failed to update packages"
fi

yum -y install git salt-minion salt https://kojipkgs.fedoraproject.org//packages/storaged/2.2.0/1.fc23/x86_64/libstoraged-2.2.0-1.fc23.x86_64.rpm https://kojipkgs.fedoraproject.org//packages/storaged/2.2.0/1.fc23/x86_64/storaged-2.2.0-1.fc23.x86_64.rpm https://kojipkgs.fedoraproject.org//packages/storaged/2.2.0/1.fc23/x86_64/storaged-lvm2-2.2.0-1.fc23.x86_64.rpm

dbus-send --system --print-reply --type=method_call --dest=org.storaged.Storaged /org/storaged/Storaged/Manager org.storaged.Storaged.Manager.EnableModules boolean:true

if [ $? -ne 0 ]; then
    error "Package installation failed"
    exit 1
fi

set +x

mkdir -p /etc/skynet

# clone and install packages
git clone https://review.gerrithub.io/skyrings/skynet
cd skynet
python setup.py install
cp src/skynetd/conf/skynet.conf /etc/skynet
cp systemd-skynetd.service /usr/lib/systemd/system/

info "Installation Completed! skynetd can be satated using \"service systemd-skynetd start\""
info "Note: This node has to be configured as salt-minion with a master"
