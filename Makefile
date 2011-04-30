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
	$(INSTALL) -m755 src/disper.py $(DESTDIR)$(DATADIR)/src
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/switcher
	$(INSTALL) -m644 src/switcher/*.py $(DESTDIR)$(DATADIR)/src/switcher
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/nvidia
	$(INSTALL) -m644 src/nvidia/*.py $(DESTDIR)$(DATADIR)/src/nvidia
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/xrandr
	$(INSTALL) -m644 src/xrandr/*.py $(DESTDIR)$(DATADIR)/src/xrandr
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/src/plugins
	$(INSTALL) -m644 src/plugins/*.py $(DESTDIR)$(DATADIR)/src/plugins
	$(INSTALL) -d $(DESTDIR)$(DATADIR)/hooks
	[ -d hooks ] && $(INSTALL) -m755 hooks/* $(DESTDIR)$(DATADIR)/hooks || echo "No hooks to install"

disper: disper.in
	sed -e "s|#PREFIX#|$(PREFIX)|" <disper.in >disper

# run this after changing command-line options in src/cli.py
# afterwards the file can be committed to the repository
disper.1: src/disper.py
	help2man --name="on-the-fly display switcher" \
		-N --section=1 --output=disper.1.tmp $<
	perl -e '$$_=join("",<STDIN>);s/\.IP\s*Actions:\s*\.IP/.SH ACTIONS\n.TP/im;print' <disper.1.tmp >disper.1.tmp.1
	cat disper.1.tmp.1 | sed 's/\(disper\|cli\)\.py/disper/g' >disper.1
	rm -f disper.1.tmp disper.1.tmp.1

clean:
	rm -f disper disper.1.tmp disper.1.tmp.1
	find . -name *.pyc -exec rm -f {} \;
	find . -name *.pyo -exec rm -f {} \;
	find . -name core -exec rm -f {} \;
	find . -name *.swp -exec rm -f {} \;

