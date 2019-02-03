################################################################################
#
# python-lumacore
#
################################################################################

PYTHON_LUMACORE_VERSION = 1.8.3
PYTHON_LUMACORE_SOURCE = luma.core-$(PYTHON_LUMACORE_VERSION).tar.gz
PYTHON_LUMACORE_SITE = https://files.pythonhosted.org/packages/88/33/9be76a139d914d2a1ec9593632d81dd277d4b7005554a9881221d2b8e3ad
PYTHON_LUMACORE_SETUP_TYPE = setuptools
PYTHON_LUMACORE_LICENSE = MIT
PYTHON_LUMACORE_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
