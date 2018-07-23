################################################################################
#
# touchui-system-apps
#
################################################################################

TOUCHUI_SYSTEM_APPS_VERSION = 6db6aeb7fbdfeacbac59f751359c31105973d80e
TOUCHUI_SYSTEM_APPS_SITE = $(call github,ski7777,TouchUI-SystemApps,$(TOUCHUI_SYSTEM_APPS_VERSION))
TOUCHUI_SYSTEM_APPS_DEPENDENCIES = touchui
TOUCHUI_SYSTEM_APPS_LICENSE = GPL-3.0
TOUCHUI_SYSTEM_APPS_LICENSE_FILES = LICENSE
TOUCHUI_SYSTEM_APPS_TARGET_DIR = $(TARGET_DIR)/opt/ftc/apps/system

define TOUCHUI_SYSTEM_APPS_INSTALL_TARGET_CMDS

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_ABOUT)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/about; \
		cp -r $(@D)/about/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/about; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_BLUETOOTH)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/bluetooth; \
		cp -r $(@D)/bluetooth/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/bluetooth; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_DISPLAY)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/display; \
		cp -r $(@D)/display/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/display; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_FTGUI)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/ftgui; \
		cp -r $(@D)/ftgui/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/ftgui; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_LANGUAGE)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/language; \
		cp -r $(@D)/language/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/language; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_NETWORK)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/network; \
		cp -r $(@D)/network/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/network; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_STORE)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/store; \
		cp -r $(@D)/store/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/store; \
	fi

	if [ "$(BR2_PACKAGE_TOUCHUI_SYSTEM_APPS_WLAN)" == "y" ]; then \
		mkdir -p $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/wlan; \
		cp -r $(@D)/wlan/* $(TOUCHUI_SYSTEM_APPS_TARGET_DIR)/wlan; \
	fi
endef

$(eval $(generic-package))
