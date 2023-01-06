################################################################################
#
# python-smbus2
#
################################################################################

PYTHON_SMBUS2_VERSION = 0.4.2
PYTHON_SMBUS2_SOURCE = smbus2-$(PYTHON_SMBUS2_VERSION).tar.gz
PYTHON_SMBUS2_SITE = https://files.pythonhosted.org/packages/7c/01/18a9c3fccc2ddc0af16ddbe52aadc4585fbd1e7ae4ee32e780abbfc7fc97
PYTHON_SMBUS2_SETUP_TYPE = setuptools
PYTHON_SMBUS2_LICENSE = MIT

$(eval $(python-package))
