export PYTHONPATH := $(shell pwd)/src/common/src:$(shell pwd)/src/master/src:$(shell pwd)/src/slave/src

test-reverse-proxy:
	cd util && python reverseProxy.py

test-master:
	cd src/master/src && python master.py ../master-sample.ini

test-slave:
	cd src/slave/src && python slave.py ../slave-sample.ini


clean:
	find . -name \*.pyc -exec rm {} \;
	find . -name \*.o -exec rm {} \;
	find . -name \*.c -exec rm {} \;
