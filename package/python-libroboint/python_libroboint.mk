################################################################################
#
# python_libroboint
#
################################################################################

PYTHON_LIBROBOINT_VERSION = 74db52ecc90c37286024a6dd30cd402f80c080db
PYTHON_LIBROBOINT_SITE = $(call github,PeterDHabermehl,libroboint-py3,$(PYTHON_LIBROBOINT_VERSION))
PYTHON_LIBROBOINT_DEPENDENCIES = libroboint

$(eval $(call ls))
