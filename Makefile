SHELL := /bin/bash
PYTHON := python
PIP := pip

BUILD_DIR := ./build
DIST_DIR := ./dist
COVER_DIR := ./_trial_temp/coverage

clean:
	find . -name "*.py[co]" -delete
	rm -f .coverage

buildclean: clean
	rm -rf $(BUILD_DIR)

distclean: clean buildclean
	rm -rf $(DIST_DIR)

coverclean: clean
	rm -rf $(COVER_DIR)

deps: py_deploy_deps py_dev_deps

py_deploy_deps: $(BUILD_DIR)/pip-deploy.log

$(BUILD_DIR)/pip-deploy.log: requirements.txt
	@mkdir -p $(BUILD_DIR)
	$(PIP) install -Ur $< && touch $@

py_dev_deps: $(BUILD_DIR)/pip-dev.log

$(BUILD_DIR)/pip-dev.log: requirements_dev.txt
	@mkdir -p $(BUILD_DIR)
	$(PIP) install -Ur $< && touch $@

unit: clean
	trial --coverage tests

test: unit

build: distclean
	python setup.py sdist bdist_egg

build_win:
	python setup.py bdist_wininst

release: distclean
	python setup.py sdist upload -r pypi
	python setup.py bdist_egg upload -r pypi
	python setup.py bdist_wininst upload -r pypi
