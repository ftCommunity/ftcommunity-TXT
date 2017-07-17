ifeq ($(BR2_PACKAGE_QT5_VERSION_LATEST),y)
QT5_VERSION_MAJOR = 5.8
QT5_VERSION = $(QT5_VERSION_MAJOR).0
QT5_SITE = http://download.qt.io/official_releases/qt/$(QT5_VERSION_MAJOR)/$(QT5_VERSION)/submodules
QT5_SNAPSHOTS_SITE = http://download.qt.io/snapshots/qt/$(QT5_VERSION_MAJOR)/$(QT5_VERSION)/latest_src/submodules
else
QT5_VERSION_MAJOR = 5.6
QT5_VERSION = $(QT5_VERSION_MAJOR).2
QT5_SITE = http://download.qt.io/official_releases/qt/$(QT5_VERSION_MAJOR)/$(QT5_VERSION)/submodules
QT5_SNAPSHOTS_SITE = http://download.qt.io/snapshots/qt/$(QT5_VERSION_MAJOR)/$(QT5_VERSION)/latest_src/submodules
endif

include $(sort $(wildcard package/qt5/*/*.mk))

define QT5_LA_PRL_FILES_FIXUP
	for i in $$(find $(STAGING_DIR)/usr/lib* -name "libQt5*.la"); do \
		$(SED)  "s:$(BASE_DIR):@BASE_DIR@:g" \
			-e "s:$(STAGING_DIR):@STAGING_DIR@:g" \
			-e "s:\(['= ]\)/usr:\\1@STAGING_DIR@/usr:g" \
			-e "s:@STAGING_DIR@:$(STAGING_DIR):g" \
			-e "s:@BASE_DIR@:$(BASE_DIR):g" \
			$$i ; \
		$(SED) "/^dependency_libs=/s%-L/usr/lib %%g" $$i ; \
	done
	for i in $$(find $(STAGING_DIR)/usr/lib* -name "libQt5*.prl"); do \
		$(SED) "s%-L/usr/lib%%" $$i; \
	done
endef

# Variable for other Qt applications to use
QT5_QMAKE = $(HOST_DIR)/usr/bin/qmake -spec devices/linux-buildroot-g++
