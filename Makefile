# simple Makefile for disper

PREFIX = /usr
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/disper

INSTALL = install

all: disper

install: disper
	$(INSTALL) -d $(DESTDIR)$(BINDIR)
	$(INSTALL) -m755 disper $(DESTDIR)$(BINDIR)
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src
	$(INSTALL) -m755 src/cli.py $(DESTDIR)$(DATADIR)/src
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/switcher
	$(INSTALL) -m644 src/switcher/*.py $(DESTDIR)$(DATADIR)/src/switcher
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/nvidia
	$(INSTALL) -m644 src/nvidia/*.py $(DESTDIR)$(DATADIR)/src/nvidia
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/xrandr
	$(INSTALL) -m644 src/xrandr/*.py $(DESTDIR)$(DATADIR)/src/xrandr

disper: disper.in
	sed -e "s|#PREFIX#|$(PREFIX)|" <disper.in >disper

# run this after changing command-line options in src/cli.py
# afterwards the file can be committed to the repository
disper.1:
	help2man --name="on-the-fly display switcher" \
		-N --section=1 --output=disper.1 ./src/cli.py

clean:
	rm -f disper

