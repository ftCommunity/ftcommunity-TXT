################################################################################
#
# python_libroboint
#
################################################################################

PYTHON_LIBROBOINT_VERSION = cf25fdba52ad1343317afca683d8b272682f0077
PYTHON_LIBROBOINT_SITE = $(call gitlab,Humpelstilzchen,libroboint,$(LIBROBOINT_VERSION))
PYTHON_LIBROBOINT_LICENSE = LGPLv2.1
PYTHON_LIBROBOINT_SUBDIR = python
PYTHON_LIBROBOINT_SETUP_TYPE = setuptools

$(eval $(python-package))
