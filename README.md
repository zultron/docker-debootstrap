= Docker debootstrap image builder

Build Docker images from debootstrap, including foreign architectures


== Prerequisites

The host kernel must have the `binfmt_misc` capability enabled, and
must have the appropriate formats (e.g. `qemu-arm`) in
`/proc/sys/fs/binfmt_misc`.

Check the kernel configuration on Ubuntu:

    cat /boot/config-`uname -r` | grep BINFMT_MISC

Install formats on Ubuntu and check:

    sudo apt-get install qemu binfmt-support
    update-binfmts --display


== Running

The `build-image.sh` script requires a distro name from the
`distros.yaml` file as the first argument. It's a good idea to set the
Docker image maintainer in the second argument. Example:

    ./build-image.sh  wheezy-rpi "Me <me@example.com>"

When the script finishes, run the image, for example:

    sudo docker run -i -t wheezy-rpi uname -m

== Principles of operation

The `distros.yaml` file contains enough information about a distro +
arch combo to build a chroot.

The `build-image.sh` script generates a `Dockerfile` in the `config`
subdirectory, and builds the image-builder Docker image.

The `build-image.sh` script then runs the `cmd.sh` script in the
image-builder, which builds the chroot filesystem with `debootstrap`.

Finally, the `build-image.sh` script imports the chroot filesystem
into a Docker image.
