#!/bin/bash
version=v$(<board/fischertechnik/TXT/rootfs/etc/fw-ver.txt)
git tag --annotate --message='new release' $version
git push upstream $version
make release
