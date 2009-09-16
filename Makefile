export PWD := $(shell pwd)
export PYTHONPATH := $(PWD)/src/common/src:$(PWD)/src/common/test:$(PWD)/src/master/src:$(PWD)/src/master/test:$(PWD)/src/slave/src
export PYTHON=/opt/local/bin/python2.6


run-reverse-proxy:
	cd util && $(PYTHON) reverseProxy.py

run-master:
	cd src/master/src && $(PYTHON) master.py ../master-sample.ini

test-master:
	cd src/master/test && $(PYTHON) test_slaveMgmt.py

run-slave:
	cd src/slave/src && $(PYTHON) slave.py ../slave-sample.ini


pythonpath:
	@echo $(PYTHONPATH)

clean:
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.o -exec rm {} \;
	find . -name \*.c -exec rm {} \;
