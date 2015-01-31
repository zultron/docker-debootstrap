if test "${DISTRIB_GPG_KEY}" != None; then
    wget $DISTRIB_GPG_KEY -O - | sudo apt-key add -
fi

# Install QEMU user emulator, if applicable
QEMU_USER_EMULATOR=/usr/bin/qemu-${DEB_HOST_ARCH_CPU}-static
if test -f $QEMU_USER_EMULATOR; then
    mkdir -p /build/usr/bin
    cp $QEMU_USER_EMULATOR /build/usr/bin
fi

debootstrap --arch=$DEB_HOST_ARCH --foreign\
    $DISTRIB_CODENAME /build \
    $DISTRIB_MIRROR
    # > /dev/null
