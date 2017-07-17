################################################################################
#
# liburcu
#
################################################################################

LIBURCU_VERSION = 0.9.2
LIBURCU_SITE = http://lttng.org/files/urcu
LIBURCU_SOURCE = userspace-rcu-$(LIBURCU_VERSION).tar.bz2
LIBURCU_LICENSE = LGPLv2.1+ (library), MIT-like (few source files listed in LICENSE), GPLv2+ (test), GPLv3 (few *.m4 files)
LIBURCU_LICENSE_FILES = lgpl-2.1.txt lgpl-relicensing.txt gpl-2.0.txt LICENSE

LIBURCU_INSTALL_STAGING = YES

$(eval $(autotools-package))
