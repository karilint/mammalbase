#!/bin/sh

# Use user given paths or just ./
[ "$*" ] \
	&& SOURCES=$* \
	|| SOURCES=./

echo Making sure that pylint and pylint_django is installed
pip -q show pylint pylint_django \
	|| pip install pylint pylint_django

echo Running pylint on paths: $SOURCES
python -m pylint \
	--load-plugins pylint_django \
	--django-settings-module=config.settings \
	$SOURCES
