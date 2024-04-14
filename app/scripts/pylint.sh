#!/bin/sh

# Use user given paths or just ./
[ "$*" ] \
	&& SOURCES=$* \
	|| SOURCES=./
# Give some feedback that something is going to happen
echo Running pylint on paths: $SOURCES
# Make sure that pylint and pylint_django plugin is installed
pip -q show pylint pylint_django \
	|| pip install pylint pylint_django
# Run pylint agains chosen paths
python -m pylint \
	--load-plugins pylint_django \
	--django-settings-module=config.settings \
	$SOURCES
