PACKAGE := "r5"


include development/*.mk

.PHONY: help check fmt lint unit coverage report

help:	## This Message
	@egrep -h '\s##\s' $(MAKEFILE_LIST)  | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

