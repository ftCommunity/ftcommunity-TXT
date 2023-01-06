################################################################################
#
# libroboint
#
################################################################################

LIBROBOINT_VERSION = 9d7cfb09386f0f63b3954fdf4043b92b259548e4
LIBROBOINT_SITE = $(call gitlab,Humpelstilzchen,libroboint,$(LIBROBOINT_VERSION))
LIBROBOINT_LICENSE = LGPLv2.1
LIBROBOINT_DEPENDENCIES = libusb
LIBROBOINT_INSTALL_TARGET_OPTS = DESTDIR=$(TARGET_DIR) LIB_LDCONFIG_CMD=true install
LIBROBOINT_MAKE_OPTS = all
LIBROBOINT_MAKE_ENV = PYTHON_ROOT=$(TARGET_DIR)

ifeq ($(BR2_PACKAGE_LIBROBOINT_PYTHON),y)
	LIBROBOINT_DEPENDENCIES += host-python3 python3
	LIBROBOINT_MAKE_OPTS += python
endif

$(eval $(cmake-package))
