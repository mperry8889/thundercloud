export PYTHONPATH := $(shell pwd)/src/lib:$(shell pwd)/src/master/src:$(shell pwd)/src/slave/src

test-reverse-proxy:
	cd util && python reverseProxy.py

test-master:
	cd src/master/src && python master.py

test-slave:
	cd src/test/src && python slave.py


clean:
	find -name \*.pyc -exec rm {} \;
	find -name \*.o -exec rm {} \;
	find -name \*.c -exec rm {} \;
