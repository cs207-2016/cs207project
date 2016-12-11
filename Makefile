sdist:
	$(MAKE) -C ./src/timeseries sdist
	$(MAKE) -C ./src/rbtree sdist

test:
	export PYTEST_ADDOPTS=' --cov-report term-missing'
	py.test

install:
	$(MAKE) sdist
	pip install ./dist/*.tar.gz

uninstall:
	pip uninstall rbtree timeseries
