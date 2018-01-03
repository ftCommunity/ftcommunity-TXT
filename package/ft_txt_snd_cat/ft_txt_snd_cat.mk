################################################################################
#
# ft_bt_remote_server
#
################################################################################

FT_TXT_SND_CAT_VERSION = 1.0.0
FT_TXT_SND_CAT_SITE = $(call github,ftCommunity,txt_snd_cat,$(FT_TXT_SND_CAT_VERSION))
FT_TXT_SND_CAT_LICENSE = GPLv3+
FT_TXT_SND_CAT_INSTALL_STAGING = NO

define FT_TXT_SND_CAT_BUILD_CMDS
        $(MAKE1) $(TARGET_CONFIGURE_OPTS) -C $(@D)
endef

define FT_TXT_SND_CAT_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 755 $(@D)/txt_snd_cat $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
