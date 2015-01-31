#!/usr/bin/python

import argparse
import yaml
import sys

class Dockerfile(object):
    distrib_map = dict(
        # codename = (distro, release)
        wheezy = ("Debian", "7.0"),
        jessie = ("Debian", "8.0"),
        trusty = ("Ubuntu", "14.04"),
        )

    deb_host_map = dict(
        # arch = deb_host_arch, deb_host_arch_cpu
        armv6l = ("armhf", "arm"),
        armv7l = ("armhf", "arm"),
        i686 = ("i686", None),
        )

    def __init__(self,
                 distro=None,
                 config="distros.yaml",
                 maintainer="Nobody <nobody@example.com>",
                 ):

        if distro is None:
            raise Exception("No distro specified")
        self.populate(distro, config)

        self.maintainer = maintainer

    @property
    def distrib_id(self):
        return self.distrib_map[self.distrib_codename][0]

    @property
    def distrib_release(self):
        return self.distrib_map[self.distrib_codename][1]

    @property
    def distrib_description(self):
        return "%s %s" % (self.distrib_id, self.distrib_release)

    @property
    def deb_host_arch(self):
        return self.deb_host_map[self.arch][0]

    @property
    def deb_host_arch_cpu(self):
        return self.deb_host_map[self.arch][1]

    @classmethod
    def load(cls, config):
        with open(config,"r") as f:
            distros = yaml.load(f)
        return distros

    @classmethod
    def list(cls, config):
        for d in cls.load(config).keys():
            print d

    def populate(self, distro_name, config):
        sys.stderr.write("Loading config for '%s' from file '%s'\n" %
                         (distro_name, config))
        distros = self.load(config)
        if not distros.has_key(distro_name):
            raise Exception("Unknown distro '%s'" % distro_name)
        distro = distros[distro_name]

        self.distrib_codename = distro['codename']
        self.arch = distro['arch']
        self.distrib_mirror = distro['mirror']
        self.distrib_gpg_key_url = distro.get('gpgkey',None)

    def render_line(self, line):
        return line % dict(
            codename = self.distrib_codename,
            id = self.distrib_id,
            release = self.distrib_release,
            description = self.distrib_description,
            mirror = self.distrib_mirror,
            gpgkey = self.distrib_gpg_key_url,
            arch = self.arch,
            deb_arch = self.deb_host_arch,
            deb_cpu = self.deb_host_arch_cpu,
            maintainer = self.maintainer,
            )

    def env(self, config="distros.yaml", distro_name=None):
        distros = self.load(config)
        if not distros.has_key(distro_name):
            raise Exception("Unknown distro '%s'" % distro_name)
        distro = distros[distro_name]
        lines = (
            "DISTRIB_CODENAME=%(codename)s",
            "DISTRIB_ID=%(id)s",
            "DISTRIB_RELEASE=%(release)s",
            "DISTRIB_DESCRIPTION=\"%(description)s\"",
            "DISTRIB_MIRROR=%(mirror)s",
            "DISTRIB_GPG_KEY=%(gpgkey)s",
            "DEB_HOST_ARCH=%(deb_arch)s",
            "DEB_HOST_ARCH_CPU=%(deb_cpu)s",
            "DEB_HOST_GNU_TYPE=linux-gnu",
            "DEB_HOST_MULTIARCH=%(deb_arch)s-%(deb_cpu)s",
            )
        for line in lines:
            print self.render_line(line)

    @property
    def lines(self):
        lines = [
            "# Build a %(description)s image",
            "#",
            "# Invoke:",
            "#     sudo docker build -t %(codename)s-%(arch)s-chroot "\
                "%(codename)s-%(arch)s",
            "#     # debootstrap requires 'privileged' mode",
            "#     sudo docker run --privileged "\
                "--volume=/host:/%(codename)s-%(arch)s \\",
            "#         %(codename)s-%(arch)s-chroot",
            "",
            "FROM ubuntu",
            "MAINTAINER %(maintainer)s",
            "",
            "ENV        DISTRIB_CODENAME %(codename)s",
            "ENV        DISTRIB_ID %(id)s",
            "ENV        DISTRIB_RELEASE %(release)s",
            "ENV        DISTRIB_DESCRIPTION \"%(description)s\"",
            "ENV        DISTRIB_MIRROR %(mirror)s",
            "ENV        DISTRIB_GPG_KEY %(gpgkey)s",
            "",
            "ENV        DEB_HOST_ARCH %(deb_arch)s",
            "ENV        DEB_HOST_ARCH_CPU %(deb_cpu)s",
            "ENV        DEB_HOST_GNU_TYPE linux-gnu",
            "ENV        DEB_HOST_MULTIARCH %(deb_arch)s-%(deb_cpu)s",
            "",
            "# Update apt",
            "RUN	apt-get update",
            "",
            "# Install packages",
            "RUN	apt-get install -y debootstrap",
            "RUN	apt-get install -y  wget",
            "RUN	apt-get install -y qemu-user-static",
            "",
            "# Import gpg key, if applicable",
            "RUN echo DISTRIB_GPG_KEY ${DISTRIB_GPG_KEY}",
            "RUN	if test \"${DISTRIB_GPG_KEY}\" != None; then \\",
            "	    wget -O - -q ${DISTRIB_GPG_KEY} | \\",
            "	        apt-key add -; \\",
            "	fi",
            "",
            "# Add cmd.sh to image",
            "ADD	cmd.sh /cmd.sh",
            "# Run cmd.sh",
            "WORKDIR	/build",
            "CMD	bash -xe /cmd.sh",
            ]
        return lines

    def write(self, fname=None):
        if fname:
            with open(fname, 'w') as f:
                for line in self.lines:
                    f.write(self.render_line(line) + '\n')
        else:
            for line in self.lines:
                print self.render_line(line)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate a Dockerfile')

    parser.add_argument('--distro', '-d',
                        help='Distribution name from config')
    parser.add_argument('--config', '-c',
                        help='Config file; default distros.yaml',
                        default='distros.yaml')
    parser.add_argument('--maintainer', '-m',
                        help='Docker image maintainer',
                        default="Nobody <nobody@example.com>")
    parser.add_argument('--output', '-o',
                        help='Output file')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List distros')
    parser.add_argument('--env', '-e', action='store_true',
                        help='Write script setting environment vars in bash')

    args = parser.parse_args()

    if args.list:
        Dockerfile.list(args.config)

    elif args.env:
        d = Dockerfile(distro=args.distro, config=args.config,
                       maintainer=args.maintainer)
        d.env(config=args.config, distro_name=args.distro)

    else:
        d = Dockerfile(distro=args.distro, config=args.config,
                       maintainer=args.maintainer)
        d.write(args.output)
