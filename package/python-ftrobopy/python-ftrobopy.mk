################################################################################
#
# python-ftrobopy
#
################################################################################

PYTHON_FTROBOPY_VERSION = caf5f38ea37b22a1f49d15d050a0242b67919ae4
PYTHON_FTROBOPY_SITE = $(call github,ftcommunity,ftrobopy,$(PYTHON_FTROBOPY_VERSION))
PYTHON_FTROBOPY_LICENSE = MIT
PYTHON_FTROBOPY_LICENSE_FILES = LICENSE
PYTHON_FTROBOPY_INSTALL_STAGING = NO
PYTHON_FTROBOPY_SETUP_TYPE = distutils

$(eval $(python-package))
