################################################################################
#
# python-ipykernel
#
################################################################################

PYTHON_IPYKERNEL_VERSION = 4.5.1
PYTHON_IPYKERNEL_SOURCE = ipykernel-$(PYTHON_IPYKERNEL_VERSION).tar.gz
PYTHON_IPYKERNEL_SITE = https://pypi.python.org/packages/23/7a/a82c599760efe61862154120fece1d877a18657cf9d9b5baf75da4931c8f
PYTHON_IPYKERNEL_SETUP_TYPE = distutils
PYTHON_IPYKERNEL_LICENSE = BSD

$(eval $(python-package))
