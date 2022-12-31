################################################################################
#
# ft_txt_snd_cat
#
################################################################################

FT_TXT_SND_CAT_SITE = $(BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH)/package/ft_txt_snd_cat
FT_TXT_SND_CAT_SITE_METHOD = local
FT_TXT_SND_CAT_DEPENDENCIES = linux

define FT_TXT_SND_CAT_BUILD_CMDS
        $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define FT_TXT_SND_CAT_INSTALL_TARGET_CMDS
        $(INSTALL) -D -m 755 $(@D)/ft_txt_snd_cat $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
