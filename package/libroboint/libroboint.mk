################################################################################
#
# libroboint
#
################################################################################

LIBROBOINT_VERSION = f99ca1204af1ffcd89bf5b0c0195590738bbb451
LIBROBOINT_SITE = $(call github,nxdefiant,libroboint,$(LIBROBOINT_VERSION))
LIBROBOINT_LICENSE = LGPLv2.1
LIBROBOINT_DEPENDENCIES = libusb host-libusb libusb-compat host-libusb-compat binutils
LIBROBOINT_CONF_OPTS = -DBUILD_DEMOS=ON
LIBROBOINT_INSTALL_TARGET_OPTS = DESTDIR=$(TARGET_DIR) LIB_LDCONFIG_CMD=true install

$(eval $(cmake-package))
