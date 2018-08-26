
all: buildroot/Makefile buildroot/.config
	make -C buildroot

buildroot/Makefile:
	git submodule update --init buildroot

buildroot/.config:
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig


