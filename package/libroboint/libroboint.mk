################################################################################
#
# libroboint
#
################################################################################

LIBROBOINT_VERSION = cf25fdba52ad1343317afca683d8b272682f0077
LIBROBOINT_SITE = $(call gitlab,Humpelstilzchen,libroboint,$(LIBROBOINT_VERSION))
LIBROBOINT_LICENSE = LGPLv2.1
LIBROBOINT_DEPENDENCIES = libusb host-libusb libusb-compat host-libusb-compat binutils

$(eval $(cmake-package))
