deps/outdated:		## Pip - Check Updates
	pip3 list --outdated

deps/install:		## Pip - Install Deps Libs
	pip3 install -r development/Require/requirements.txt
