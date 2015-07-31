#! /bin/sh

coverage run -m --include=. --source=. --omit=bitcoincrawler/test -m `ls -1 bitcoincrawler/test/test*.py|sed -e "s/\//./"|sed -e "s/\.py//"`

coverage report
coverage html
coverage xml
