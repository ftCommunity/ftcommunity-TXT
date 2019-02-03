################################################################################
#
# python-lumaled_matrix
#
################################################################################

PYTHON_LUMALED_MATRIX_VERSION = 1.1.1
PYTHON_LUMALED_MATRIX_SOURCE = luma.led_matrix-$(PYTHON_LUMALED_MATRIX_VERSION).tar.gz
PYTHON_LUMALED_MATRIX_SITE = https://files.pythonhosted.org/packages/43/ad/592dff62a2962a73674e714eddd0e388758030d5b82cb88999adca0c0e89
PYTHON_LUMALED_MATRIX_SETUP_TYPE = setuptools
PYTHON_LUMALED_MATRIX_LICENSE = MIT
PYTHON_LUMALED_MATRIX_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
