################################################################################
#
# python-jupyter_core
#
################################################################################

PYTHON_JUPYTER_CORE_VERSION = 4.2.0
PYTHON_JUPYTER_CORE_SOURCE = jupyter_core-$(PYTHON_JUPYTER_CORE_VERSION).tar.gz
PYTHON_JUPYTER_CORE_SITE = https://pypi.python.org/packages/56/41/6b29a0646af48ee7545b0b488b1b00aa3b01f6b4a8f19e3339640982a694
PYTHON_JUPYTER_CORE_SETUP_TYPE = distutils
PYTHON_JUPYTER_CORE_LICENSE = BSD

$(eval $(python-package))
