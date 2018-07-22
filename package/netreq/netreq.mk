################################################################################
#
# netreq
#
################################################################################

NETREQ_SITE = $(BR2_EXTERNAL_FTCOMMUNITY_TXT_PATH)/package/netreq
NETREQ_SITE_METHOD = local
NETREQ_DEPENDENCIES = libnetfilter_queue

define NETREQ_BUILD_CMDS
   $(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define NETREQ_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 $(@D)/netreq $(TARGET_DIR)/usr/bin
endef

$(eval $(generic-package))
