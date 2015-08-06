#! /bin/sh
. venv/bin/activate
nosetests --with-coverage --cover-erase --cover-package=bitcoincrawler --cover-html
