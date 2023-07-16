project/fmt:		## App - Code Style - Format
	black -v $(PACKAGE)/

project/lint:		## App - Code Style - Lint
	pylint --fail-under=9 $(PACKAGE)

project/check:		## App - Run Tests
	make project/fmt project/lint project/coverage

project/coverage:	## App - Test - Coverage
	 coverage run -m pytest  && coverage report -m

project/coverage/report:		## App - Test - Coverage Report
	 coverage xml

project/install:	## App - Install
	python3 setup.py install
	$(MAKE) project/clean

project/clean:		## App - Clean
	python3 setup.py clean
	rm -rf $(PACKAGE).egg-info dist build
	rm -rf $(OUTPUT_DIRECTORY)

project/venv:	## App - Create Virtual Environment
	python3 -m venv venv/