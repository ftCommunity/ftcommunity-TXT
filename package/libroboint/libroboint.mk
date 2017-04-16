################################################################################
#
# libroboint
#
################################################################################

LIBROBOINT_VERSION = f99ca1204af1ffcd89bf5b0c0195590738bbb451
LIBROBOINT_SITE = $(call github,nxdefiant,libroboint,$(LIBROBOINT_VERSION))
LIBROBOINT_LICENSE = LGPLv2.1
LIBROBOINT_DEPENDENCIES = libusb libusb-compat
LIBROBOINT_CONF_OPTS = -DBUILD_DEMOS=ON

$(eval $(cmake-package))
