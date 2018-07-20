################################################################################
#
# upmpdcli
#
################################################################################

UPMPDCLI_VERSION = 1.2.16
UPMPDCLI_SITE = http://www.lesbonscomptes.com/upmpdcli/downloads
UPMPDCLI_LICENSE = GPL-2.0+
UPMPDCLI_LICENSE_FILES = COPYING
UPMPDCLI_DEPENDENCIES = host-pkgconf libmpdclient libupnpp libmicrohttpd jsoncpp

# Upmpdcli only runs if user upmpdcli exists
define UPMPDCLI_USERS
	upmpdcli -1 upmpdcli -1 * - - audio Upmpdcli MPD UPnP Renderer Front-End
endef

define UPMPDCLI_INSTALL_INIT_SYSV
	$(INSTALL) -D -m 0755 package/upmpdcli/S99upmpdcli $(TARGET_DIR)/etc/init.d/S99upmpdcli
endef

define UPMPDCLI_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 644 $(@D)/systemd/upmpdcli.service \
		$(TARGET_DIR)/usr/lib/systemd/system/upmpdcli.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -sf ../../../../usr/lib/systemd/system/upmpdcli.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/upmpdcli.service
endef

define UPMPDCLI_INSTALL_CONF_FILE
	$(INSTALL) -D -m 0755 $(@D)/src/upmpdcli.conf-dist $(TARGET_DIR)/etc/upmpdcli.conf
endef

UPMPDCLI_POST_INSTALL_TARGET_HOOKS += UPMPDCLI_INSTALL_CONF_FILE

$(eval $(autotools-package))
