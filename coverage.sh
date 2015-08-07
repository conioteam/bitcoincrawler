#! /bin/sh
. venv/bin/activate
rm .coverage
coverage run --include=. --source=. --omit=venv/**,bitcoincrawler/test/**,virtualenv/**,bitcoincrawler/components/model.py,bitcoincrawler/components/node_backend.py,bitcoincrawler/observers.py  `which nosetests`

coverage report
coverage html
coverage xml

