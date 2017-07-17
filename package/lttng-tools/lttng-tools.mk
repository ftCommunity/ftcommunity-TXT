################################################################################
#
# lttng-tools
#
################################################################################

LTTNG_TOOLS_VERSION = 2.9.3
LTTNG_TOOLS_SITE = http://lttng.org/files/lttng-tools
LTTNG_TOOLS_SOURCE = lttng-tools-$(LTTNG_TOOLS_VERSION).tar.bz2
LTTNG_TOOLS_LICENSE = GPLv2+, LGPLv2.1+ (include/lttng/*, src/lib/lttng-ctl/*)
LTTNG_TOOLS_LICENSE_FILES = gpl-2.0.txt lgpl-2.1.txt LICENSE
LTTNG_TOOLS_CONF_OPTS += --disable-man-pages

LTTNG_TOOLS_DEPENDENCIES = liburcu libxml2 popt util-linux

ifeq ($(BR2_PACKAGE_LTTNG_LIBUST),y)
LTTNG_TOOLS_CONF_OPTS += --with-lttng-ust
LTTNG_TOOLS_DEPENDENCIES += lttng-libust
else
LTTNG_TOOLS_CONF_OPTS += --without-lttng-ust
endif

$(eval $(autotools-package))
