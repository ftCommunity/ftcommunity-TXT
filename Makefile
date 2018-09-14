
all: buildroot/Makefile buildroot/.config
	make -C buildroot

clean:
	BR2_EXTERNAL=.. make -C buildroot clean

buildroot/Makefile:
	git submodule update --init buildroot

buildroot/.config:
	BR2_EXTERNAL=.. make -C buildroot fischertechnik_TXT_defconfig

zipdir = build

release:
	if [ ! -f $(imagedir)/rootfs.img ]; then make; fi
	$(eval version := $(shell cat buildroot/output/target/etc/fw-ver.txt))
	$(eval zipfile := $(zipdir)/ftcommunity-txt-$(version).zip)
	$(eval imagedir := buildroot/output/images)
	mkdir -p $(zipdir)
	rm -f $(zipfile)
	zip -j $(zipfile) $(imagedir)/am335x-kno_txt.dtb $(imagedir)/rootfs.img $(imagedir)/uImage
