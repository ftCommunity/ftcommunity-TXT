################################################################################
#
# libroboint
#
################################################################################

LIBROBOINT_VERSION = cf25fdba52ad1343317afca683d8b272682f0077
LIBROBOINT_SITE = $(call gitlab,Humpelstilzchen,libroboint,$(LIBROBOINT_VERSION))
LIBROBOINT_LICENSE = LGPLv2.1
LIBROBOINT_DEPENDENCIES = libusb host-libusb libusb-compat host-libusb-compat binutils
LIBROBOINT_INSTALL_TARGET_OPTS = DESTDIR=$(TARGET_DIR) LIB_LDCONFIG_CMD=true install
LIBROBOINT_MAKE_OPTS = all
LIBROBOINT_MAKE_ENV = PYTHON_ROOT=$(TARGET_DIR)

ifeq ($(BR2_PACKAGE_LIBROBOINT_PYTHON),y)
	LIBROBOINT_DEPENDENCIES += host-python3 python3
	LIBROBOINT_MAKE_OPTS += python
endif

$(eval $(cmake-package))
