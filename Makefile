# store the current working directory
CWD := $(shell pwd)
BASEDIR := $(CWD)
PRINT_STATUS = export EC=$$?; cd $(CWD); if [ "$$EC" -eq "0" ]; then printf "SUCCESS!\n"; else exit $$EC; fi
VERSION   = $(shell grep __version__ src/skynetd/__init__.py | sed "s/.*= '\(.*\)'/\1/")

BUILDS    := .build
DEPLOY    := $(BUILDS)/deploy
TARDIR    := skynet-$(VERSION)
RPMBUILD  := $(HOME)/rpmbuild


dist:
	rm -fr $(HOME)/$(BUILDS)
	mkdir -p $(HOME)/$(BUILDS) $(RPMBUILD)/SOURCES
	cp -fr $(BASEDIR) $(HOME)/$(BUILDS)/$(TARDIR)
	cd $(HOME)/$(BUILDS); \
	tar --exclude-vcs --exclude=.* -zcf skynet-$(VERSION).tar.gz $(TARDIR); \
	cp skynet-$(VERSION).tar.gz $(RPMBUILD)/SOURCES
	# Cleaning the work directory
	rm -fr $(HOME)/$(BUILDS)


rpm:
	@echo "target: rpm"
	@echo  "  ...building rpm $(V_ARCH)..."
	rm -fr $(BUILDS)
	mkdir -p $(DEPLOY)/latest
	mkdir -p $(RPMBUILD)/SPECS
	sed -e "s/@VERSION@/$(VERSION)/" skynet.spec \
		> $(RPMBUILD)/SPECS/skynet.spec
	rpmbuild -ba $(RPMBUILD)/SPECS/skynet.spec
	$(PRINT_STATUS); \
	if [ "$$EC" -eq "0" ]; then \
		FILE=$$(readlink -f $$(find $(RPMBUILD)/RPMS -name skynet-$(VERSION)*.rpm)); \
		cp -f $$FILE $(DEPLOY)/latest/; \
		printf "\nThe Skyring RPMs are located at:\n\n"; \
		printf "   $(DEPLOY)/latest\n\n\n\n"; \
	fi
