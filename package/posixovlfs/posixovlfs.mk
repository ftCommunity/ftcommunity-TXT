################################################################################
#
# POSIXOVLFS
#
################################################################################

POSIXOVLFS_VERSION = 740fb233bd1f7ca6cc77190703982a76aff51ad9
POSIXOVLFS_SITE = git://git.code.sf.net/p/posixovl/posixovl
POSIXOVLFS_LICENSE = GPLv2+
POSIXOVLFS_DEPENDENCIES = libfuse attr
POSIXOVLFS_AUTORECONF=YES
POSIXOVLFS_INSTALL_TARGET_OPTS=DESTDIR=$(TARGET_DIR) install-exec

$(eval $(autotools-package))
