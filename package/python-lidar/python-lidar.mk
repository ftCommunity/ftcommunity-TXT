################################################################################
#
# python-lidar
#
################################################################################

PYTHON_LIDAR_VERSION = 1.0.4
PYTHON_LIDAR_SOURCE = v$(PYTHON_LIDAR_VERSION).tar.gz
PYTHON_LIDAR_SITE = https://github.com/Gadgetoid/VL53L0X-python/archive/refs/tags
#https://github.com/johnbryanmoore/VL53L0X_rasp_python/archive/refs/tags
PYTHON_LIDAR_SETUP_TYPE = setuptools
PYTHON_LIDAR_LICENSE = MIT
PYTHON_LIDAR_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))

#define PYTHON_LIDAR_BUILD_CMDS
#    $(MAKE) $(TARGET_CONFIGURE_OPTS) PYTHON_INCLUDES= -C $(@D) all
#endef
#$(eval $(generic-package))
