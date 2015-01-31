#!/bin/bash -xe

DOCKERFILE_GEN=`dirname $0`/dockerfile_gen.py
DISTRO=$1
test -z "$2" || MAINTAINER_ARG="-m '$2'"
CONFIG=`dirname $0`/distros.yaml
CONFIG_DIR=`dirname $0`/config
CHROOT_DIR=`dirname $0`/$DISTRO

echo "Setting up chroot directory in $CHROOT_DIR" >&2
mkdir -p $CHROOT_DIR

echo "Setting up $CONFIG_DIR" >&2
rm -rf $CONFIG_DIR && mkdir -p $CONFIG_DIR
install -m 755 cmd.sh $CONFIG_DIR
python $DOCKERFILE_GEN -d $DISTRO $MAINTAINER_ARG \
    -c $CONFIG -o $CONFIG_DIR/Dockerfile

echo "Building the container builder" >&2
sudo docker build -t $DISTRO-builder $CONFIG_DIR

echo "Running the container builder" >&2
sudo docker run --privileged \
    --volume=$(readlink -f $CHROOT_DIR):/build \
    $DISTRO-builder

echo "Importing new image ${DISTRO}" >&2
sudo tar -C $CHROOT_DIR -c . | \
    sudo docker import - ${DISTRO}
