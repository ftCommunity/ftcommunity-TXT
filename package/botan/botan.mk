################################################################################
#
# botan
#
################################################################################

BOTAN_VERSION = 1.10.16
BOTAN_SOURCE = Botan-$(BOTAN_VERSION).tgz
BOTAN_SITE = http://botan.randombit.net/releases
BOTAN_LICENSE = BSD-2c
BOTAN_LICENSE_FILES = doc/license.txt

BOTAN_INSTALL_STAGING = YES

BOTAN_CONF_OPTS = \
	--cpu=$(BR2_ARCH) \
	--os=linux \
	--cc=gcc \
	--cc-bin="$(TARGET_CXX)" \
	--prefix=/usr

ifeq ($(BR2_STATIC_LIBS),y)
BOTAN_CONF_OPTS += --disable-shared --no-autoload
endif

ifeq ($(BR2_PACKAGE_BZIP2),y)
BOTAN_DEPENDENCIES += bzip2
BOTAN_CONF_OPTS += --with-bzip2
endif

ifeq ($(BR2_PACKAGE_GMP),y)
BOTAN_DEPENDENCIES += gmp
BOTAN_CONF_OPTS += --with-gnump
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
BOTAN_DEPENDENCIES += openssl
BOTAN_CONF_OPTS += --with-openssl
endif

ifeq ($(BR2_PACKAGE_ZLIB),y)
BOTAN_DEPENDENCIES += zlib
BOTAN_CONF_OPTS += --with-zlib
endif

ifeq ($(BR2_POWERPC_CPU_HAS_ALTIVEC),y)
BOTAN_CONF_OPTS += --enable-altivec
else
BOTAN_CONF_OPTS += --disable-altivec
endif

define BOTAN_CONFIGURE_CMDS
	(cd $(@D); $(TARGET_MAKE_ENV) ./configure.py $(BOTAN_CONF_OPTS))
endef

define BOTAN_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) AR="$(TARGET_AR) crs"
endef

define BOTAN_INSTALL_STAGING_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR="$(STAGING_DIR)/usr" install
endef

define BOTAN_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR="$(TARGET_DIR)/usr" install
endef

$(eval $(generic-package))
