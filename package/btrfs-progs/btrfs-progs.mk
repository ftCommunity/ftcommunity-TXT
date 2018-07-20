################################################################################
#
# btrfs-progs
#
################################################################################

BTRFS_PROGS_VERSION = 4.16
BTRFS_PROGS_SITE = $(BR2_KERNEL_MIRROR)/linux/kernel/people/kdave/btrfs-progs
BTRFS_PROGS_SOURCE = btrfs-progs-v$(BTRFS_PROGS_VERSION).tar.xz
BTRFS_PROGS_DEPENDENCIES = host-pkgconf e2fsprogs lzo util-linux zlib
BTRFS_PROGS_CONF_OPTS = --disable-backtrace --disable-zstd --disable-python
BTRFS_PROGS_LICENSE = GPL-2.0, LGPL-3.0+ (libbtrfsutil)
BTRFS_PROGS_LICENSE_FILES = COPYING libbtrfsutil/COPYING \
	libbtrfsutil/COPYING.LESSER
BTRFS_PROGS_INSTALL_STAGING = YES

# Doesn't autodetect static-only and tries to build both
ifeq ($(BR2_STATIC_LIBS),y)
BTRFS_PROGS_MAKE_OPTS = static
BTRFS_PROGS_INSTALL_TARGET_OPTS = DESTDIR=$(TARGET_DIR) install-static
BTRFS_PROGS_INSTALL_STAGING_OPTS = DESTDIR=$(STAGING_DIR) install-static
endif

$(eval $(autotools-package))
