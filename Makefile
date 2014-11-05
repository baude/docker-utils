SHELL = /bin/sh


DESTDIR="/"

install:
	python setup.py build
	python setup.py install --root=$(DESTDIR)
	mkdir -p $(DESTDIR)/var/container-template/system
	mkdir -p $(DESTDIR)/var/container-template/user
	chgrp -R docker $(DESTDIR)/var/container-template
	chmod -R 775 $(DESTDIR)/var/container-template

