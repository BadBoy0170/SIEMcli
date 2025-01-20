   

# Makefile for siemcli
# https://github.com/dogoncouch/siemcli

all: install clean

default: all

install:
	python2 setup.py install

clean:
	rm -rf build dist siemcli.egg-info
