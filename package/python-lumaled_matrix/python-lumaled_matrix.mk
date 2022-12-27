################################################################################
#
# python-lumaled_matrix
#
################################################################################

PYTHON_LUMALED_MATRIX_VERSION = 1.7.0
PYTHON_LUMALED_MATRIX_SOURCE = luma.led_matrix-$(PYTHON_LUMALED_MATRIX_VERSION).tar.gz
PYTHON_LUMALED_MATRIX_SITE = https://files.pythonhosted.org/packages/cc/41/8cf7078e77da1ededef2bcc958114afc52725e948b01f16fa3542c914bbd
PYTHON_LUMALED_MATRIX_SETUP_TYPE = setuptools
PYTHON_LUMALED_MATRIX_LICENSE = MIT
PYTHON_LUMALED_MATRIX_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
