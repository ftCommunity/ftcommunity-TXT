################################################################################
#
# qt5canvas3d
#
################################################################################

QT5CANVAS3D_VERSION = $(QT5_VERSION)
QT5CANVAS3D_SITE = $(QT5_SITE)
QT5CANVAS3D_SOURCE = qtcanvas3d-$(QT5_SOURCE_TARBALL_PREFIX)-$(QT5CANVAS3D_VERSION).tar.xz
QT5CANVAS3D_DEPENDENCIES = qt5base qt5declarative
QT5CANVAS3D_INSTALL_STAGING = YES

QT5CANVAS3D_LICENSE = GPL-2.0 or GPL-3.0 or LGPL-3.0
QT5CANVAS3D_LICENSE_FILES = LICENSE.GPLv2 LICENSE.GPLv3 LICENSE.LGPLv3

define QT5CANVAS3D_CONFIGURE_CMDS
	(cd $(@D); $(TARGET_MAKE_ENV) $(HOST_DIR)/bin/qmake)
endef

define QT5CANVAS3D_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)
endef

define QT5CANVAS3D_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) install
	$(QT5_LA_PRL_FILES_FIXUP)
endef

define QT5CANVAS3D_INSTALL_TARGET_CMDS
	cp -dpfr $(STAGING_DIR)/usr/qml/QtCanvas3D $(TARGET_DIR)/usr/qml/
endef

$(eval $(generic-package))
