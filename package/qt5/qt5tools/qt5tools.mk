################################################################################
#
# qt5tools
#
################################################################################

QT5TOOLS_VERSION = $(QT5_VERSION)
QT5TOOLS_SITE = $(QT5_SITE)
QT5TOOLS_SOURCE = qttools-opensource-src-$(QT5BASE_VERSION).tar.xz

QT5TOOLS_DEPENDENCIES = qt5base
QT5TOOLS_INSTALL_STAGING = YES

# linguist tools compile conditionally on qtHaveModule(qmldevtools-private),
# but the condition is used only used to decide if lupdate will support
# parsing qml files (via setting QT_NO_QML define), no linking against
# target qt5 will happen
ifeq ($(BR2_PACKAGE_QT5DECLARATIVE),y)
QT5TOOLS_DEPENDENCIES += qt5declarative
endif

ifeq ($(BR2_PACKAGE_QT5BASE_LICENSE_APPROVED),y)
ifeq ($(BR2_PACKAGE_QT5_VERSION_LATEST),y)
QT5TOOLS_LICENSE = GPLv2+ or LGPLv3, GPLv3 with exception(tools), GFDLv1.3 (docs)
QT5TOOLS_LICENSE_FILES = LICENSE.GPL2 LICENSE.GPLv3 LICENSE.LGPLv3 LICENSE.FDL
else
QT5TOOLS_LICENSE = GPLv3 or LGPLv2.1 with exception or LGPLv3, GFDLv1.3 (docs)
QT5TOOLS_LICENSE_FILES = LICENSE.GPLv3 LICENSE.LGPLv21 LGPL_EXCEPTION.txt LICENSE.LGPLv3 LICENSE.FDL
endif
else
QT5TOOLS_LICENSE = Commercial license
QT5TOOLS_REDISTRIBUTE = NO
endif

QT5TOOLS_BUILD_DIRS_$(BR2_PACKAGE_QT5TOOLS_LINGUIST_TOOLS) += \
	linguist/lconvert linguist/lrelease linguist/lupdate
ifeq ($(BR2_PACKAGE_QT5TOOLS_LINGUIST_TOOLS),y)
# use install target to copy cmake module files
define QT5TOOLS_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/src/linguist install
endef
endif

QT5TOOLS_BUILD_DIRS_$(BR2_PACKAGE_QT5TOOLS_PIXELTOOL) += pixeltool
QT5TOOLS_INSTALL_TARGET_$(BR2_PACKAGE_QT5TOOLS_PIXELTOOL) += pixeltool

QT5TOOLS_BUILD_DIRS_$(BR2_PACKAGE_QT5TOOLS_QTDIAG) += qtdiag
QT5TOOLS_INSTALL_TARGET_$(BR2_PACKAGE_QT5TOOLS_QTDIAG) += qtdiag

QT5TOOLS_BUILD_DIRS_$(BR2_PACKAGE_QT5TOOLS_QTPATHS) += qtpaths
QT5TOOLS_INSTALL_TARGET_$(BR2_PACKAGE_QT5TOOLS_QTPATHS) += qtpaths

QT5TOOLS_BUILD_DIRS_$(BR2_PACKAGE_QT5TOOLS_QTPLUGININFO) += qtplugininfo
QT5TOOLS_INSTALL_TARGET_$(BR2_PACKAGE_QT5TOOLS_QTPLUGININFO) += qtplugininfo

define QT5TOOLS_CONFIGURE_CMDS
	(cd $(@D); $(TARGET_MAKE_ENV) $(HOST_DIR)/usr/bin/qmake)
endef

define QT5TOOLS_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) sub-src-qmake_all
	$(foreach p,$(QT5TOOLS_BUILD_DIRS_y), \
		$(TARGET_MAKE_ENV) $(MAKE) -C $(@D)/src/$(p)$(sep))
endef

define QT5TOOLS_INSTALL_TARGET_CMDS
	$(foreach p,$(QT5TOOLS_INSTALL_TARGET_y), \
		$(INSTALL) -D -m0755 $(@D)/bin/$(p) $(TARGET_DIR)/usr/bin/$(p)$(sep))
endef

$(eval $(generic-package))
