export PWD := $(shell pwd)
export PYTHONPATH := $(PWD)/test:$(PWD)/src/common/src:$(PWD)/src/common/test:$(PWD)/src/master/src:$(PWD)/src/master/test:$(PWD)/src/slave/src
export PYTHON=/opt/local/bin/python2.6
export TRIAL=/opt/local/bin/trial-2.6

run-reverse-proxy:
	cd util && $(PYTHON) reverseProxy.py

run-master:
	cd src/master/src && $(PYTHON) master.py ../master-sample.ini

run-slave:
	cd src/slave/src && $(PYTHON) slave.py ../slave-sample.ini

unit-test:
	$(TRIAL) --logfile $(PWD)/build/unit-test.log --coverage `find src -name test_\*py`

test: unit-test

pythonpath:
	@echo $(PYTHONPATH)

clean:
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.o -exec rm {} \;
	rm -rf build/*
	rm -rf _trial_temp

.PHONY: test
