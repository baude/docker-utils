SHELL = /bin/sh


PREFIX = $(DESTDIR)/usr
BINDIR = $(PREFIX)/bin
 
objects = docker-dash.py container-template.py docker_wrapper.py metadata.py
TARGET = $(objects)


install:
	for files in $(objects); do \
		command=$$( echo "$$files" | sed 's/\.py//'); \
		install -D $$files $(BINDIR)/$$command; \
		chmod 755 $(BINDIR)/$$command; \
	done
	install -D
	mkdir -p $(DESTDIR)/var/container-template/system
	mkdir $(DESTDIR)/var/container-template/user

uninstall: docker-dash.py
	for files in $(objects); do \
		command=$$( echo "$$files" | sed 's/\.py//'); \
		rm $(BINDIR)/$$command; \
	done


