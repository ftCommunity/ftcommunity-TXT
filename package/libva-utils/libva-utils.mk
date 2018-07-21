################################################################################
#
# libva-utils
#
################################################################################

LIBVA_UTILS_VERSION = 2.1.0
LIBVA_UTILS_SOURCE = libva-utils-$(LIBVA_UTILS_VERSION).tar.bz2
LIBVA_UTILS_SITE = https://github.com/01org/libva-utils/releases/download/$(LIBVA_UTILS_VERSION)
LIBVA_UTILS_LICENSE = MIT
LIBVA_UTILS_LICENSE_FILES = COPYING
LIBVA_UTILS_DEPENDENCIES = host-pkgconf libva

$(eval $(autotools-package))
