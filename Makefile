SHELL := /bin/bash
PYTHON := python
PIP := pip

BUILD_DIR := ./build
DIST_DIR := ./dist
COVER_DIR := ./_trial_temp/coverage
EGG := ./txnats.egg-info


clean:
	find . -name "*.py[co]" -delete

buildclean: clean 
	rm -rf $(BUILD_DIR)

distclean: clean buildclean
	rm -rf $(DIST_DIR)
	rm -rf $(EGG)
	rm -rf ./txnatsc

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

build-for-example: clean 
	python setup.py build
	rm -rf example/txnats
	cp -R $(BUILD_DIR)/lib/txnats example/ 

prepare-example: build-for-example buildclean

update-readme:
	pandoc -f markdown -t rst -o .generated_README.rst README.md

register: distclean build update-readme
	python setup.py register

release: distclean update-readme
	python setup.py sdist upload -r pypi
	python setup.py bdist_egg upload -r pypi
	python setup.py bdist_wininst upload -r pypi
