################################################################################
#
# alsa-lib
#
################################################################################

ALSA_LIB_VERSION = 1.1.3
ALSA_LIB_SOURCE = alsa-lib-$(ALSA_LIB_VERSION).tar.bz2
ALSA_LIB_SITE = ftp://ftp.alsa-project.org/pub/lib
ALSA_LIB_LICENSE = LGPLv2.1+ (library), GPLv2+ (aserver)
ALSA_LIB_LICENSE_FILES = COPYING aserver/COPYING
ALSA_LIB_INSTALL_STAGING = YES
ALSA_LIB_CFLAGS = $(TARGET_CFLAGS)
ALSA_LIB_AUTORECONF = YES
ALSA_LIB_CONF_OPTS = \
	--with-alsa-devdir=$(call qstrip,$(BR2_PACKAGE_ALSA_LIB_DEVDIR)) \
	--with-pcm-plugins="$(call qstrip,$(BR2_PACKAGE_ALSA_LIB_PCM_PLUGINS))" \
	--with-ctl-plugins="$(call qstrip,$(BR2_PACKAGE_ALSA_LIB_CTL_PLUGINS))" \
	--without-versioned

# Can't build with static & shared at the same time (1.0.25+)
ifeq ($(BR2_STATIC_LIBS),y)
ALSA_LIB_CONF_OPTS += \
	--enable-shared=no \
	--without-libdl
else
ALSA_LIB_CONF_OPTS += --enable-static=no
endif

ifneq ($(BR2_PACKAGE_ALSA_LIB_ALOAD),y)
ALSA_LIB_CONF_OPTS += --disable-aload
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_MIXER),y)
ALSA_LIB_CONF_OPTS += --disable-mixer
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_PCM),y)
ALSA_LIB_CONF_OPTS += --disable-pcm
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_RAWMIDI),y)
ALSA_LIB_CONF_OPTS += --disable-rawmidi
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_HWDEP),y)
ALSA_LIB_CONF_OPTS += --disable-hwdep
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_SEQ),y)
ALSA_LIB_CONF_OPTS += --disable-seq
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_ALISP),y)
ALSA_LIB_CONF_OPTS += --disable-alisp
endif
ifneq ($(BR2_PACKAGE_ALSA_LIB_OLD_SYMBOLS),y)
ALSA_LIB_CONF_OPTS += --disable-old-symbols
endif

ifeq ($(BR2_PACKAGE_ALSA_LIB_PYTHON),y)
ALSA_LIB_CONF_OPTS += \
	--with-pythonlibs=-lpython$(PYTHON_VERSION_MAJOR) \
	--with-pythonincludes=$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)
ALSA_LIB_CFLAGS += -I$(STAGING_DIR)/usr/include/python$(PYTHON_VERSION_MAJOR)
ALSA_LIB_DEPENDENCIES = python
else
ALSA_LIB_CONF_OPTS += --disable-python
endif

ifeq ($(BR2_bfin),y)
# blackfin external toolchains don't have versionsort. Fake it using alphasort
# instead
ALSA_LIB_CFLAGS += -Dversionsort=alphasort
endif

ALSA_LIB_CONF_ENV = \
	CFLAGS="$(ALSA_LIB_CFLAGS)" \
	LDFLAGS="$(TARGET_LDFLAGS) -lm"

$(eval $(autotools-package))
