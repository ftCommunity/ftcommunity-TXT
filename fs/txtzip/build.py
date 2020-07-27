#!/usr/bin/env python3

import sys
import os

f = open(os.environ["BR2_CONFIG"], "r")
vars = dict([(l.split("=", 1)[0], l.split("=", 1)[1].strip().strip('"'))
             for l in f.readlines() if (not l.startswith("#")) and l.strip() != ""])
f.close()

confpath = os.path.expandvars(vars["BR2_TARGET_ROOTFS_TXTZIP_CONFIG"])
fsdir = os.environ["ROOTFS_TXTZIP_DIR"]
imagedir = os.environ["BINARIES_DIR"]


def presentAndYes(name):
    if name in vars:
        if vars[name] == "y":
            return True
    return False


custom = False
if presentAndYes("BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME"):
    custom = True
    extension = vars["BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_EXTENSION"]
    if presentAndYes("BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_SOURCE_STRING"):
        name = vars["BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_NAME"]
    else:
        f = open(os.path.expandvars(vars["BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_SOURCE_FILE_NAME"]))
        base = f.readline().strip()
        f.close()
        name = vars["BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_PREFIX"] + \
            base+vars["BR2_TARGET_ROOTFS_TXTZIP_CUSTOM_NAME_SUFFIX"]

if not custom:
    name = "txtzip"
    extension = "zip"

workdir = os.path.join(fsdir, name)
zippath = os.path.join(imagedir, name + "." + extension)
outdir = os.path.join(imagedir, name)


print("Cleaning up")
os.system("rm -rf " + workdir + "; mkdir " + workdir)
os.system("rm -rf " + zippath + " " + outdir)

print("Copying files")
conffile = open(confpath, 'r')
for l in conffile.readlines():
    l = l.strip()
    if "->" in l:
        sp = l.split("->")
        s = sp[0]
        t = sp[1]
        s = os.path.expandvars(s)
        f = os.path.basename(s)
        t = os.path.join(workdir, t)

    else:
        s = l
        s = os.path.expandvars(s)
        f = os.path.basename(s)
        t = os.path.join(workdir, f)
    td = os.path.dirname(t)
    os.system("mkdir -p " + td)
    os.system("cp -r " + s + " " + t)

print("Copying output directory")
os.system("cp -r " + workdir + " " + outdir)

print("zipping files")
os.system("cd " + workdir + "; zip -r " + zippath + " *")
