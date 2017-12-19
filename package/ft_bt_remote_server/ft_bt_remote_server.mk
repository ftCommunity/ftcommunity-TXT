################################################################################
#
# ft_bt_remote_server
#
################################################################################

FT_BT_REMOTE_SERVER_VERSION = 9df88db2676cf1364e85a373889183ff21c4922e
FT_BT_REMOTE_SERVER_SITE = $(call github,ftCommunity,ft_bt_remote_server,$(FT_BT_REMOTE_SERVER_VERSION))
FT_BT_REMOTE_SERVER_LICENSE = GPLv3+
FT_BT_REMOTE_SERVER_INSTALL_STAGING = NO
FT_BT_REMOTE_SERVER_DEPENDENCIES += bluez_utils

define FT_BT_REMOTE_SERVER_BUILD_CMDS
        $(MAKE1) $(TARGET_CONFIGURE_OPTS) -C $(@D)
endef

define FT_BT_REMOTE_SERVER_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 755 $(@D)/ft_bt_remote_start.sh $(TARGET_DIR)/usr/bin
        $(INSTALL) -D -m 755 $(@D)/src/ft_bt_remote_server $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
