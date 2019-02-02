################################################################################
#
# python-smbus2
#
################################################################################

PYTHON_SMBUS2_VERSION = 0.2.3
PYTHON_SMBUS2_SOURCE = smbus2-$(PYTHON_SMBUS2_VERSION).tar.gz
PYTHON_SMBUS2_SITE = https://files.pythonhosted.org/packages/20/21/fd4e359bd130c09a728c8549fccabf3be70ea08ca7c7c6b5822faf97dcf3
PYTHON_SMBUS2_SETUP_TYPE = setuptools
PYTHON_SMBUS2_LICENSE = MIT

$(eval $(python-package))
