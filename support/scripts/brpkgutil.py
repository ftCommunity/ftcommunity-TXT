# Copyright (C) 2010-2013 Thomas Petazzoni <thomas.petazzoni@free-electrons.com>

import logging
import sys
import subprocess


# Execute the "make <pkg>-show-version" command to get the version of a given
# list of packages, and return the version formatted as a Python dictionary.
def get_version(pkgs):
    logging.info("Getting version for %s" % pkgs)
    cmd = ["make", "-s", "--no-print-directory"]
    for pkg in pkgs:
        cmd.append("%s-show-version" % pkg)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    output = p.communicate()[0]
    if p.returncode != 0:
        logging.error("Error getting version %s" % pkgs)
        sys.exit(1)
    output = output.split("\n")
    if len(output) != len(pkgs) + 1:
        logging.error("Error getting version")
        sys.exit(1)
    version = {}
    for i in range(0, len(pkgs)):
        pkg = pkgs[i]
        version[pkg] = output[i]
    return version


def _get_depends(pkgs, rule):
    logging.info("Getting dependencies for %s" % pkgs)
    cmd = ["make", "-s", "--no-print-directory"]
    for pkg in pkgs:
        cmd.append("%s-%s" % (pkg, rule))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    output = p.communicate()[0]
    if p.returncode != 0:
        logging.error("Error getting dependencies %s\n" % pkgs)
        sys.exit(1)
    output = output.split("\n")
    if len(output) != len(pkgs) + 1:
        logging.error("Error getting dependencies")
        sys.exit(1)
    deps = {}
    for i in range(0, len(pkgs)):
        pkg = pkgs[i]
        pkg_deps = output[i].split(" ")
        if pkg_deps == ['']:
            deps[pkg] = []
        else:
            deps[pkg] = pkg_deps
    return deps


# Execute the "make <pkg>-show-depends" command to get the list of
# dependencies of a given list of packages, and return the list of
# dependencies formatted as a Python dictionary.
def get_depends(pkgs):
    return _get_depends(pkgs, 'show-depends')


# Execute the "make <pkg>-show-rdepends" command to get the list of
# reverse dependencies of a given list of packages, and return the
# list of dependencies formatted as a Python dictionary.
def get_rdepends(pkgs):
    return _get_depends(pkgs, 'show-rdepends')
