################################################################################
#
# python-pillow
#
################################################################################

PYTHON_PILLOW_VERSION = c01f51dfff07416aba5f9bd78717be1887f67868
PYTHON_PILLOW_SITE = $(call github,python-pillow,Pillow,$(PYTHON_PILLOW_VERSION))
PYTHON_PILLOW_LICENSE = MIT
PYTHON_PILLOW_LICENSE_FILES = LICENSE
PYTHON_PILLOW_SETUP_TYPE = setuptools

$(eval $(python-package))
