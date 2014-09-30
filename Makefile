SHELL = /bin/sh
 

PREFIX = /usr
BINDIR = $(PREFIX)/bin
 
objects = docker-dash.py docker-wrapper.py docker-createjson.py
TARGET = $(objects)


install:
	for files in $(objects); do \
		command=$$( echo "$$files" | sed 's/\.py//'); \
		install -D $$files $(BINDIR)/$$command; \
		chmod 755 $(BINDIR)/$$command; \
	done
 

uninstall: docker-dash.py
	for files in $(objects); do \
		command=$$( echo "$$files" | sed 's/\.py//'); \
		rm $(BINDIR)/$$command; \
	done


