################################################################################
#
# python_libroboint
#
################################################################################

PYTHON_LIBROBOINT_VERSION = b4dda4e5bad4f828096f44904c98f597b7c13be3
PYTHON_LIBROBOINT_SITE = $(call github,PeterDHabermehl,libroboint-py3,$(PYTHON_LIBROBOINT_VERSION))
PYTHON_LIBROBOINT_DEPENDENCIES = libroboint

define PYTHON_LIBROBOINT_INSTALL_PY_STUFF
	$(INSTALL) -D -m 0644 $(@D)/robointerface.py $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/robointerface.py
endef
PYTHON_LIBROBOINT_POST_INSTALL_TARGET_HOOKS += PYTHON_LIBROBOINT_INSTALL_PY_STUFF

$(eval $(generic-package))

