#! /bin/sh

coverage run --include=. --source=. --omit=bitcoincrawler/test/**,virtualenv/** `which nosetests`

coverage report
coverage html
coverage xml
