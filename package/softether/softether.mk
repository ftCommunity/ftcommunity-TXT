################################################################################
#
# softether
#
################################################################################

SOFTETHER_VERSION = 1e17c9bcfd7e7b31756aa5389bcbff76c2c9c88a
SOFTETHER_SITE = $(call github,SoftEtherVPN,SoftEtherVPN,$(SOFTETHER_VERSION))
SOFTETHER_PATCH = \
	https://github.com/dajhorn/SoftEtherVPN/commit/c5e5d7e93c6f3302adf5821c29c4efdb7630e418.patch \
	https://github.com/dajhorn/SoftEtherVPN/commit/75625af541fd128f51079d0ffe5ef24645b8f421.patch
SOFTETHER_LICENSE = GPLv2
SOFTETHER_LICENSE_FILES = LICENSE
SOFTETHER_DEPENDENCIES = host-softether openssl readline
SOFTETHER_AUTORECONF = YES

ifeq ($(BR2_ENABLE_LOCALE),)
SOFTETHER_DEPENDENCIES += libiconv
SOFTETHER_CONF_ENV = LIBS+=" -liconv"
endif

ifeq ($(BR2_STATIC_LIBS),y)
# openssl needs zlib
SOFTETHER_CONF_ENV += LIBS+=" -lz"
endif

SOFTETHER_CONF_OPTS = \
	--with-openssl="$(STAGING_DIR)/usr" \
	--with-zlib="$(STAGING_DIR)/usr"

# host-libiconv does not exist, therefore we need this extra line
HOST_SOFTETHER_DEPENDENCIES = host-pkgconf host-openssl host-readline

# target build creates the file hamcore.se2 which needs the host variant of
# hamcorebuilder, for details see http://www.vpnusers.com/viewtopic.php?p=5426
define HOST_SOFTETHER_BUILD_CMDS
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D)/src/Mayaqua
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D)/src/Cedar
	$(HOST_MAKE_ENV) $(MAKE) -C $(@D)/src/hamcorebuilder
endef

define HOST_SOFTETHER_INSTALL_CMDS
	$(INSTALL) -m 0755 $(@D)/src/hamcorebuilder/hamcorebuilder $(HOST_DIR)/usr/bin/hamcorebuilder
endef

$(eval $(autotools-package))
$(eval $(host-autotools-package))
