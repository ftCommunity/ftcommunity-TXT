################################################################################
#
# python-lumaoled
#
################################################################################

PYTHON_LUMAOLED_VERSION = 3.9.0
PYTHON_LUMAOLED_SOURCE = luma.oled-$(PYTHON_LUMAOLED_VERSION).tar.gz
PYTHON_LUMAOLED_SITE = https://files.pythonhosted.org/packages/8d/cc/f2f0b1a10f6b3655bcd609c007e119acc0cbf0f880ec3812616336287ddc
PYTHON_LUMAOLED_SETUP_TYPE = setuptools
PYTHON_LUMAOLED_LICENSE = MIT
PYTHON_LUMAOLED_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
