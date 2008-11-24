# simple Makefile for disper

PREFIX = $(DESTDIR)/usr
BINDIR = $(PREFIX)/bin
DATADIR = $(PREFIX)/share/disper

all: disper

install: disper
	$(INSTALL) -d $(BINDIR)
	$(INSTALL) -m755 disper $(BINDIR)
	$(INSTALL) -d $(DATADIR)
	$(INSTALL) -m755 main.py $(DATADIR)
	$(INSTALL) -d $(DATADIR)/switcher $(DATADIR)/nvidia $(DATADIR)/xrandr
	$(INSTALL) -m644 switcher/*.py $(DATADIR)/switcher
	$(INSTALL) -m644 nvidia/*.py $(DATADIR)/nvidia
	$(INSTALL) -m644 xrandr/*.py $(DATADIR)/xrandr

disper: disper.in
	sed -e "s|#PREFIX#|$(PREFIX)|" <disper.in >disper

clean:
	rm -f disper

