SHELL = /bin/sh


ifdef DESTDIR
	DESTDIR := "fofofo"
endif

DESTDIR="/"

install:
	python setup.py build
	python setup.py install --root=$(DESTDIR)
	python setup.py install_lib 
	mkdir -p $(DESTDIR)/var/container-template/system
	mkdir -p $(DESTDIR)/var/container-template/user
	chgrp -R docker $(DESTDIR)/var/container-template
	chmod -R 775 $(DESTDIR)/var/container-template

