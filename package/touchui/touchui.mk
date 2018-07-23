################################################################################
#
# touchui
#
################################################################################

TOUCHUI_VERSION = b0b8d9d9b9451e7a7b5f75631eb74cd9329de4fd
TOUCHUI_SITE = $(call github,ski7777,TouchUI,$(TOUCHUI_VERSION))
TOUCHUI_DEPENDENCIES = qt python-pyqt
TOUCHUI_LICENSE = GPL-3.0
TOUCHUI_LICENSE_FILES = LICENSE
TOUCHUI_TARGET_DIR = $(TARGET_DIR)/opt/ftc
TOUCHUI_TARGET_USER = $(subst ",,$(BR2_PACKAGE_TOUCHUI_USER))

define TOUCHUI_CONFIGURE_CMDS
	sed -i 's/$$USER/$(TOUCHUI_TARGET_USER)/' $(@D)/support/TouchUI.initd
	if [ "$(BR2_PACKAGE_TOUCHUI_VNC_ENABLE)" == "y" ]; then \
		sed -i 's/#export DISPLAY="multi: \$${DISPLAY} VNC:0"/export DISPLAY="multi: \$${DISPLAY} VNC:0"/g' $(@D)/support/TouchUI.initd; \
	fi
endef

define TOUCHUI_INSTALL_TARGET_CMDS
	mkdir -p $(TOUCHUI_TARGET_DIR)
	cp -r $(@D)/src/* $(TOUCHUI_TARGET_DIR)
	mkdir -p $(TOUCHUI_TARGET_DIR)/apps
	mkdir -p $(TARGET_DIR)/home/$(TOUCHUI_TARGET_USER)/apps/
	$(INSTALL) -D $(@D)/support/config $(TARGET_DIR)/etc/default/touchui
	ln -s -f ../../../home/$(TOUCHUI_TARGET_USER)/apps/ $(TARGET_DIR)/opt/ftc/apps/user
	if [ "$(BR2_PACKAGE_TOUCHUI_INITD_ENABLE)" == "y" ]; then \
		if [ ! -z $(BR2_PACKAGE_TOUCHUI_INITD_NAME) ]; then \
			$(INSTALL) -D -m 0755 $(@D)/support/TouchUI.initd $(TARGET_DIR)/etc/init.d/$(BR2_PACKAGE_TOUCHUI_INITD_NAME); \
		fi \
	fi
endef

define TOUCHUI_PERMISSIONS
	/opt/ftc/apps                           d       755     $(TOUCHUI_TARGET_USER)    $(TOUCHUI_TARGET_USER)    -       -       -       -       -
	/etc/default/touchui                   f       644     $(TOUCHUI_TARGET_USER)    $(TOUCHUI_TARGET_USER)    -       -       -       -       -
endef

$(eval $(generic-package))
