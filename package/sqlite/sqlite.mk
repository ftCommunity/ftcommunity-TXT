################################################################################
#
# sqlite
#
################################################################################

SQLITE_VERSION = 3220000
SQLITE_SOURCE = sqlite-autoconf-$(SQLITE_VERSION).tar.gz
SQLITE_SITE = http://www.sqlite.org/2018
SQLITE_LICENSE = Public domain
SQLITE_LICENSE_FILES = tea/license.terms
SQLITE_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_SQLITE_STAT3),y)
SQLITE_CFLAGS += -DSQLITE_ENABLE_STAT3
endif

ifeq ($(BR2_PACKAGE_SQLITE_ENABLE_COLUMN_METADATA),y)
SQLITE_CFLAGS += -DSQLITE_ENABLE_COLUMN_METADATA
endif

ifeq ($(BR2_PACKAGE_SQLITE_ENABLE_FTS3),y)
SQLITE_CFLAGS += -DSQLITE_ENABLE_FTS3
endif

ifeq ($(BR2_PACKAGE_SQLITE_ENABLE_JSON1),y)
SQLITE_CFLAGS += -DSQLITE_ENABLE_JSON1
endif

ifeq ($(BR2_PACKAGE_SQLITE_ENABLE_UNLOCK_NOTIFY),y)
SQLITE_CFLAGS += -DSQLITE_ENABLE_UNLOCK_NOTIFY
endif

ifeq ($(BR2_PACKAGE_SQLITE_SECURE_DELETE),y)
SQLITE_CFLAGS += -DSQLITE_SECURE_DELETE
endif

ifeq ($(BR2_PACKAGE_SQLITE_NO_SYNC),y)
SQLITE_CFLAGS += -DSQLITE_NO_SYNC
endif

# fallback to standard -O3 when -Ofast is present to avoid -ffast-math
SQLITE_CFLAGS += $(subst -Ofast,-O3,$(TARGET_CFLAGS))

SQLITE_CONF_ENV = CFLAGS="$(SQLITE_CFLAGS)"

ifeq ($(BR2_STATIC_LIBS),y)
SQLITE_CONF_OPTS += --enable-dynamic-extensions=no
else
SQLITE_CONF_OPTS += --disable-static-shell
endif

ifeq ($(BR2_TOOLCHAIN_HAS_THREADS),y)
SQLITE_CONF_OPTS += --enable-threadsafe
else
SQLITE_CONF_OPTS += --disable-threadsafe
endif

ifeq ($(BR2_PACKAGE_NCURSES)$(BR2_PACKAGE_READLINE),yy)
SQLITE_DEPENDENCIES += ncurses readline
SQLITE_CONF_OPTS += --disable-editline --enable-readline
else ifeq ($(BR2_PACKAGE_LIBEDIT),y)
SQLITE_DEPENDENCIES += libedit
SQLITE_CONF_OPTS += --enable-editline --disable-readline
else
SQLITE_CONF_OPTS += --disable-editline --disable-readline
endif

$(eval $(autotools-package))
$(eval $(host-autotools-package))
