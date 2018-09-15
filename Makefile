
all: buildroot/Makefile buildroot/.config
	make -C buildroot

clean:
	BR2_EXTERNAL=.. make -C buildroot clean

buildroot/Makefile:
	git submodule update --init buildroot

CONFIG_DEPENDS = \
  .gitmodules \
  board/fischertechnik/TXT/tisdk_am335x-fischertechnik_txt_defconfig

buildroot/.config: $(CONFIG_DEPENDS)
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig


