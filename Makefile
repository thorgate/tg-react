.PHONY: help clean clean-build clean-pyc lint black test test-all test-full coverage docs update-messages add-locale

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "test-full - shorthand for test lint coverage"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "update-messages - Update translation files"
	@echo "add-locale - Add a new translation locale"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	prospector

black:
	black demo dummy_settings.py tg_react

test:
	pytest

test-all:
	tox

test-full: test lint coverage

coverage:
	pytest --cov-config .coveragerc --cov=tg_react --cov-report html --cov-report term-missing

docs:
	mkdir -p docs/_static
	sphinx-apidoc -o docs/ tg_react
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

tg_react/locale:
	mkdir -p tg_react/locale

update-messages: tg_react/locale
	cd tg_react && django-admin makemessages -a && django-admin compilemessages

add-locale: tg_react/locale
ifdef LOCALE
	@echo "Adding new locale $(LOCALE)"
	cd tg_react && django-admin makemessages -l $(LOCALE)
else
	@echo "\033[31;01mPlease specify the locale you would like to add via LOCALE (e.g. LOCALE='et' make add-locale)\033[0m"
endif
