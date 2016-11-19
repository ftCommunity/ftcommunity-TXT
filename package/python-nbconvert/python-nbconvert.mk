################################################################################
#
# python-nbconvert
#
################################################################################

PYTHON_NBCONVERT_VERSION = 5.0.0b1
PYTHON_NBCONVERT_SOURCE = nbconvert-$(PYTHON_NBCONVERT_VERSION).tar.gz
PYTHON_NBCONVERT_SITE = https://pypi.python.org/packages/48/ea/1fe38e9616c6b35e4f7c535c2fb62bed01b96df89fd07ec128518a0a46b1
PYTHON_NBCONVERT_SETUP_TYPE = distutils
PYTHON_NBCONVERT_LICENSE = BSD

$(eval $(python-package))
